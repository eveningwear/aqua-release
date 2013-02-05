"""
	codex.py

	Used to query from and post build information to Codex Web Service

	Written by: Marc Kubischta, Eric Robinson
	Contributions from: Jochen Hagenstrom, Chris Loveless

	The Codex database is accessed through a web service currently located on
	matrix.corp.adobe.com.  There is a test server on anderson.corp.adobe.com.
	Calls to the Codex can be made using SOAP.  For Python, using SOAP requires
	a couple of extra modules not included with the standard distribution:

	ZSI - The SOAP module we will be using

		Can be obtained from:  http://pywebsvcs.sourcefourge.net

	These modules are also checked into Perforce on yorktown.corp.adobe.com:1820 at
	//releases/tools/codex/webservice/...

	You can also find the latest version of this file at that location.  Contact Eric
	Robinson for access to this Perforce server.

	In this module, we define a class: CodexService, which we will use to make our calls
	to post to the web service (or query from it).  This class contains paths to the WSDL
	files published by the web service, which ZSI uses to define the list of methods
	available to us through the Codex web service.

	Posting to Codex:

	The most important method in the class is postBuild().  This is the method used to actually
	upload our data to Codex.  The other important method is setUserName(),which MUST be called
	before calling postBuild().  The username is the same used to access the Codex website,
	typically your ADOBENET username.

	Querying from Codex:

	For querying from Codex, the simplest method is queryDependencies().  This method
	calls the web service, which returns an XML formatted list of specific builds
	that should be integrated into a given product, version, and platform.
	We take this XML and parse it into a list of Build objects with the data we want.  The
	Build object is defined below, and is basically just a list of attributes.  No
	methods are currently defined.
			
"""
import sys, os.path, shutil
from xml.dom.minidom import parseString
from ZSI import ServiceProxy, FaultException
import codexdatatypes as datatypes

#webserviceserver = "http://localhost:7070"
#webserviceserver = "http://10.32.190.43:7070"
#webserviceserver = "http://kitn2.corp.adobe.com:8080"
#webserviceserver = "http://munin.corp.adobe.com:8080"
webserviceserver = "http://codex.corp.adobe.com"

class CodexService(object):
	"""
		Class used to connect to Codex web service.
		See https://zerowing.corp.adobe.com/display/codex/Codex+2.0+API+Specification
	"""

	def __init__(self, tracefile=None):
		"""
			The init method.  The web service has one WSDL file that is of interest
			to us, codex.wsdl. Both methods for posting and retrieving information
			via Codex are defined by it.
		"""

		# First, see if there's a ".service_proxy_dir folder, and delete it.
		# Otherwise, ZSI will always go there for the WSDL instead of looking
		# to the server
		if os.path.isdir(".service_proxy_dir"):
			shutil.rmtree(".service_proxy_dir")

		wsdlfile = "%s/codex/codex.wsdl" % (webserviceserver)
		self._prodserver = ServiceProxy.ServiceProxy(wsdlfile, wsdlfile, tracefile=tracefile)

	# product class

	def getProducts(self):
		'returns a list of Products'
		try:
			result = self._prodserver.GetProducts(val='')
		except FaultException, e:
			_handleFaultException(e)
		return _getProductListFromNode(result['productlist'])

	def getProductByName(self, name):
		'returns a Product with the matching name'
		try:
			result = self._prodserver.GetProductByName(productname=name)
		except FaultException, e:
			_handleFaultException(e)
		return _getProductFromNode(result['product'])

	def getProductByID(self, id):
		'returns a Product with the matching id'
		id = int(id)
		try:
			result = self._prodserver.GetProductById(productid=id)
		except FaultException, e:
			_handleFaultException(e)
		return _getProductFromNode(result['product'])

	def addProduct(self, name, type, user, password, ticket=None):
		'creates a product of the given name and type and returns the id as an int'
		try:
			result = self._prodserver.AddProduct(productname=name, producttypename=type, ldapcredentials={'userid':user, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['productid']
		
	def deleteProduct(self, id, user, password, ticket=None):
		'deletes a product by id and returns a boolean success result'
		id=int(id)
		try:
			result = self._prodserver.DeleteProduct(productid=id, ldapcredentials={'userid':user, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['operationresult']
		
	def setProductType(self, id, type, user, password, ticket=None):
		"updates a product's type and returns the updated Product"
		id = int(id)
		try:
			result = self._prodserver.SetProductType(productid=id, producttypename=type, ldapcredentials={'userid':user, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return _getProductFromNode(result['product'])
		
	def setProductLink(self, id, link, user, password, ticket=None):
		"updates a product's link and returns the updated Product"
		id = int(id)
		try:
			result = self._prodserver.SetProductLink(productid=id, link=link, ldapcredentials={'userid':user, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return _getProductFromNode(result['product'])

	def setProductDescription(self, id, description, user, password, ticket=None):
		"updates a product's description and returns the updated Product"
		id = int(id)
		try:
			result = self._prodserver.SetProductDescription(productid=id, description=description, ldapcredentials={'userid':user, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return _getProductFromNode(result['product'])
	
	def setProductName(self, id, name, user, password, ticket=None):
		"updates a product's name and returns the updated Product"
		id = int(id)
		try:
			result = self._prodserver.SetProductName(productid=id, productname=name, ldapcredentials={'userid':user, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return _getProductFromNode(result['product'])


	# subproduct

	def addSubproduct(self, name, product, version, user, password):
		"adds a subproduct and returns the new id"
		try:
			result = self._prodserver.AddSubproduct(subproductname=name, productname=product, versionname=version, ldapcredentials={'userid':user, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['id']

	def getAllSubproducts(self):
		"gets a list of all the subproducts"
		try:
			result = self._prodserver.GetAllSubproducts(val='')
		except FaultException, e:
			_handleFaultException(e)
		return _getSubproductListFromNode(result['subproductlist'])

	def getSubproducts(self, product, version):
		"gets a list of the subproducts of a particular product version"
		try:
			result = self._prodserver.GetSubproducts(productname=product, versionname=version)
		except FaultException, e:
			_handleFaultException(e)
		return _getSubproductListFromNode(result['subproductlist'])

	def getSubproductByName(self, name, product, version):
		"gets a specific subproduct from a particular product version"
		try:
			result = self._prodserver.GetSubproductByName(subproductname=name, productname=product, versionname=version)
		except FaultException, e:
			_handleFaultException(e)
		return _getSubproductFromNode(result['subproduct'])

	def getSubproductByID(self, id):
		"gets a specific subproduct by its id"
		id = int(id)
		try:
			result = self._prodserver.GetSubproductById(id=id)
		except FaultException, e:
			_handleFaultException(e)
		return _getSubproductFromNode(result['subproduct'])

	def setSubproductDescription(self, id, description, user, password):
		"sets a subproduct's description and returns the updated subproduct"
		id = int(id)
		try:
			result = self._prodserver.SetSubproductDescription(id=id, description=description, ldapcredentials={'userid':user, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return _getSubproductFromNode(result['subproduct'])

	def setSubproductName(self, id, name, user, password):
		"sets a subproduct's name and returns the updated subproduct"
		id = int(id)
		try:
			result = self._prodserver.SetSubproductName(id=id, subproductname=name, ldapcredentials={'userid':user, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return _getSubproductFromNode(result['subproduct'])

	def deleteSubproduct(self, id, user, password):
		"deletes a subproduct by id and returns the operation result"
		id = int(id)
		try:
			result = self._prodserver.DeleteSubproduct(id=id, ldapcredentials={'userid':user, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['operationresult']


	# version class	

	def getVersions(self, product):
		'returns a list of Versions in the given product'
		try:
			result = self._prodserver.GetVersions(productname=product)
		except FaultException, e:
			_handleFaultException(e)
		return _getVersionListFromNode(result['versionlist'])

	def getAllVersions(self):
		'returns a list of all Versions'
		try:
			result = self._prodserver.GetAllVersions(val='')
		except FaultException, e:
			_handleFaultException(e)
		return _getVersionListFromNode(result['versionlist'])

	def getVersionByName(self, product, version):
		'returns a Version by name'
		try:
			result = self._prodserver.GetVersionByName(productname=product, versionname=version)
		except FaultException, e:
			_handleFaultException(e)
		return _getVersionFromNode(result['version'])

	def getVersionByID(self, id):
		'returns a Version having the specified version id'
		id=int(id)
		try:
			result = self._prodserver.GetVersionById(versionid=id)
		except FaultException, e:
			_handleFaultException(e)
		return _getVersionFromNode(result['version'])

	def addVersion(self, product, version, user, password, ticket=None):
		'creates a new version and returns its id as an int'
		try:
			result = self._prodserver.AddVersion(productname=product, versionname=version, ldapcredentials={'userid':user, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['versionid']

	def deleteVersion(self, id, user, password, ticket=None):
		'deletes a version by id and returns a boolean success result'
		id=int(id)
		try:
			result = self._prodserver.DeleteVersion(versionid=id, ldapcredentials={'userid':user, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['operationresult']

	def setVersionCodeName(self, id, codename, user, password, ticket=None):
		"updates a version's codename and returns the updated Version"
		id=int(id)
		try:
			result = self._prodserver.SetVersionCodeName(versionid=id, versioncodename=codename, ldapcredentials={'userid':user, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return _getVersionFromNode(result['version'])

	def setVersionLink(self, id, link, user, password, ticket=None):
		"updates a version's link and returns the updated Version"
		id=int(id)
		try:
			result = self._prodserver.SetVersionLink(versionid=id, link=link, ldapcredentials={'userid':user, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return _getVersionFromNode(result['version'])

	def setVersionDescription(self, id, description, user, password, ticket=None):
		"updates a version's description and returns the updated Version"
		id=int(id)
		try:
			result = self._prodserver.SetVersionDescription(versionid=id, description=description, ldapcredentials={'userid':user, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return _getVersionFromNode(result['version'])

	def setVersionName(self, id, name, user, password, ticket=None):
		"updates a version's name and returns the updated Version"
		id=int(id)
		try:
			result = self._prodserver.SetVersionName(versionid=id, versionname=name, ldapcredentials={'userid':user, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return _getVersionFromNode(result['version'])


	# certification level
	

	def getCertLevels(self):
		'returns a list of all CertLevels in codex'
		try:
			result = self._prodserver.GetCertificationLevels(val='')
		except FaultException, e:
			_handleFaultException(e)
		return _getCertLevelListFromNode(result['certificationlevellist'])

	def getCertLevelByName(self, name):
		'returns a codex CertLevel referenced by name'
		try:
			result = self._prodserver.GetCertificationLevelByName(name=name)
		except FaultException, e:
			_handleFaultException(e)
		return _getCertLevelFromNode(result['certificationlevel'])

	def getCertLevelByID(self, id):	
		'returns a codex CertLevel referenced by int id'
		id=int(id)
		try:
			result = self._prodserver.GetCertificationLevelById(id=id)
		except FaultException, e:
			_handleFaultException(e)
		return _getCertLevelFromNode(result['certificationlevel'])


	# Status

	def getStatuses(self):
		'returns a list of all Statuses in codex'
		try:
			result = self._prodserver.GetStatuses(val='')
		except FaultException, e:
			_handleFaultException(e)
		return _getStatusListFromNode(result['statuslist'])

	def getStatusByName(self, name):
		'returns a codex Status referenced by name'
		try:
			result = self._prodserver.GetStatusByName(statusname=name)
		except FaultException, e:
			_handleFaultException(e)
		return _getStatusFromNode(result['status'])

	def getStatusByID(self, id):
		'returns a codex Status referenced by int id'
		id=int(id)
		try:
			result = self._prodserver.GetStatusById(id=id)
		except FaultException, e:
			_handleFaultException(e)
		return _getStatusFromNode(result['status'])


	# Compiler Target

	def getCompilerTargets(self):
		'returns a list of all CompilerTargets in codex'
		try:
			result = self._prodserver.GetCompilerTargets(val='')
		except FaultException, e:
			_handleFaultException(e)
		return _getCompilerTargetListFromNode(result['compilertargetlist'])

	def getCompilerTargetByName(self, name):
		'returns a codex CompilerTarget referenced by name'
		try:
			result = self._prodserver.GetCompilerTargetByName(name=name)
		except FaultException, e:
			_handleFaultException(e)
		return _getCompilerTargetFromNode(result['compilertarget'])

	def getCompilerTargetByID(self, id):
		'returns a codex CompilerTarget referenced by int id'
		id=int(id)
		try:
			result = self._prodserver.GetCompilerTargetById(id=id)
		except FaultException, e:
			_handleFaultException(e)
		return _getCompilerTargetFromNode(result['compilertarget'])


	# License Model

	def getLicenseModels(self):
		'returns a list of all LicenseModels in codex'
		try:
			result = self._prodserver.GetLicenseModels(val='')
		except FaultException, e:
			_handleFaultException(e)
		return _getLicenseModelListFromNode(result['licensemodellist'])

	def getLicenseModelByName(self, name):
		'returns a codex LicenseModel referenced by name'
		try:
			result = self._prodserver.GetLicenseModelByName(name=name)
		except FaultException, e:
			_handleFaultException(e)
		return _getLicenseModelFromNode(result['licensemodel'])

	def getLicenseModelByID(self, id):
		'returns a codex LicenseModel referenced by int id'
		id=int(id)
		try:
			result = self._prodserver.GetLicenseModelById(id=id)
		except FaultException, e:
			_handleFaultException(e)
		return _getLicenseModelFromNode(result['licensemodel'])


	# Format

	def getFormats(self):
		'returns a list of all Formats in codex'
		try:
			result = self._prodserver.GetFormats(val='')
		except FaultException, e:
			_handleFaultException(e)
		return _getFormatListFromNode(result['formatlist'])

	def getFormatByName(self, name):
		'returns a codex Format referenced by name'
		try:
			result = self._prodserver.GetFormatByName(name=name)
		except FaultException, e:
			_handleFaultException(e)
		return _getFormatFromNode(result['format'])

	def getFormatByID(self, id):
		'returns a codex Format referenced by int id'
		id=int(id)
		try:
			result = self._prodserver.GetFormatById(id=id)
		except FaultException, e:
			_handleFaultException(e)
		return _getFormatFromNode(result['format'])


	# Platforms

	def getPlatforms(self):
		'returns a list of all Platforms in codex'
		try:
			result = self._prodserver.GetPlatforms(val='')
		except FaultException, e:
			_handleFaultException(e)
		return _getPlatformListFromNode(result['platformlist'])

	def getPlatformByName(self, name):
		'returns a codex Platform referenced by name'
		try:
			result = self._prodserver.GetPlatformByName(name=name)
		except FaultException, e:
			_handleFaultException(e)
		return _getPlatformFromNode(result['platform'])

	def getPlatformByID(self, id):
		'returns a codex Platform referenced by int id'
		id=int(id)
		try:
			result = self._prodserver.GetPlatformById(id=id)
		except FaultException, e:
			_handleFaultException(e)
		return _getPlatformFromNode(result['platform'])


	# Platform Groups

	def getPlatformGroups(self, product, version):
		'returns PlatformGroups for the given product/version'
		try:
			result = self._prodserver.GetPlatformgroups(productname=product, versionname=version)
		except FaultException, e:
			_handleFaultException(e)
		return _getPlatformGroupListFromNode(result['platformgrouplist'])

	def getPlatformGroupByName(self, product, version, name):
		'returns a PlatformGroup by name from the given product/version'
		try:
			result = self._prodserver.GetPlatformgroupByName(productname=product, versionname=version, platformgroupname=name)
		except FaultException, e:
			_handleFaultException(e)
		return _getPlatformGroupFromNode(result['platformgroup'])

	def getPlatformGroupByID(self, id):
		'returns a PlatformGroup by id from the given product/version'
		id=int(id)
		try:
			result = self._prodserver.GetPlatformgroupById(id=id)
		except FaultException, e:
			_handleFaultException(e)
		return _getPlatformGroupFromNode(result['platformgroup'])

	def addPlatformGroup(self, product, version, name, username, password):
		'adds a PlatformGroup to the given product/version'
		try:
			result = self._prodserver.AddPlatformgroup(productname=product, versionname=version, platformgroupname=name,
				ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['id']

	def deletePlatformGroup(self, id, username, password):
		'removes a PlatformGroup by ID'
		id=int(id)
		try:
			result = self._prodserver.DeletePlatformgroup(id=id, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['operationresult']

	def addPlatformGroupPlatform(self, id, platform, username, password):
		'adds a platform by name to the PlatformGroup specified by id'
		id=int(id)
		try:
			result = self._prodserver.AddPlatformgroupPlatform(id=id, platformname=platform,
				ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['id']

	def deletePlatformGroupPlatform(self, id, platform, username, password):
		'removes a platform by name from the PlatformGroup specified by id'
		id=int(id)
		try:
			result = self._prodserver.DeletePlatformgroupPlatform(id=id, platformname=platform,
				ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['operationresult']


	# Contacts

	def getContacts(self, product, version):
		"Gets the list of Contacts in Codex for the given Product/Version"
		try:
			result = self._prodserver.GetContacts(versionname=version, productname=product)
		except FaultException, e:
			_handleFaultException(e)
		return _getContactListFromNode(result['contactlist'])

	def getContactByName(self, product, version, name):
		"Gets the Contact record for the given Product/Version, by name"
		try:
			result = self._prodserver.GetContactByName(versionname=version, productname=product, contactname=name)
		except FaultException, e:
			_handleFaultException(e)
		return _getContactFromNode(result['contact'])

	def getContactTypes(self):
		"Gets a list of Contact Types defined in Codex"
		try:
			result = self._prodserver.GetContacttypes(val='')
		except FaultException, e:
			_handleFaultException(e)
		return _getContactTypeListFromNode(result['contacttypelist'])

	def addContact(self, product, version, name, type, username, password):
		"Adds a new Contact record to Codex for the given product/version"
		try:
			result = self._prodserver.AddContact(contactname=name, contacttypename=type, 
				versionname=version, productname=product, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['id']

	def deleteContact(self, id, username, password):
		"Deletes a contact from Codex"
		id=int(id)
		try:
			result = self._prodserver.DeleteContact(id=id, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['operationresult']


	# Languages

	def getLanguages(self):
		'returns a list of all Languages in codex'
		try:
			result = self._prodserver.GetLanguages(var='')
		except FaultException, e:
			_handleFaultException(e)
		return _getLanguageListFromNode(result['languagelist'])

	def getLanguageByName(self, name):
		'returns a codex Language referenced by name'
		try:
			result = self._prodserver.GetLanguageByName(name=name)
		except FaultException, e:
			_handleFaultException(e)
		return _getLanguageFromNode(result['language'])

	def getLanguageByID(self, id):
		'returns a codex Language referenced by int id'
		id = int(id)
		try:
			result = self._prodserver.GetLanguageById(id=id)
		except FaultException, e:
			_handleFaultException(e)
		return _getLanguageFromNode(result['language'])

	def getLanguageByCode(self, code):
		'returns a codex Language referenced by iso code'
		try:
			result = self._prodserver.GetLanguageByCode(languagecode=code)
		except FaultException, e:
			_handleFaultException(e)
		return _getLanguageFromNode(result['language'])


	# Product Types

	def getProductTypes(self):
		"Gets a list of all Producttypes defined in Codex"
		try:
			result = self._prodserver.GetProducttypes(val='')
		except FaultException, e:
			_handleFaultException(e)
		return _getProductTypeListFromNode(result['producttypelist'])

	def getProductTypeByName(self, name):
		"Gets a product type by name"
		try:
			result = self._prodserver.GetProducttypeByName(producttypename=name)
		except FaultException, e:
			_handleFaultException(e)
		return _getProductTypeFromNode(result['producttype'])

	def getProductTypeByID(self, id):
		"Gets a product type by its ID"
		id=int(id)
		try:
			result = self._prodserver.GetProducttypeById(id=id)
		except FaultException, e:
			_handleFaultException(e)
		return _getProductTypeFromNode(result['producttype'])


	# Pickup Options

	def getPickupOptions(self):
		"Gets a list of all PickupOptions defined in Codex"
		try:
			result = self._prodserver.GetPickupOptions(val='')
		except FaultException, e:
			_handleFaultException(e)
		return _getPickupOptionListFromNode(result['pickupoptionlist'])


	# Servers

	def getServers(self):
		"Gets a list of all Servers defined in Codex."
		try:
			result = self._prodserver.GetServers(val='')
		except FaultException, e:
			_handleFaultException(e)
		return _getServerListFromNode(result['serverlist'])

	def getServerByName(self, servername):
		"Gets a Server record by name."
		try:
			result = self._prodserver.GetServerByName(servername=servername)
		except FaultException, e:
			_handleFaultException(e)
		return _getServerFromNode(result['server'])

	def getServerByID(self, id):
		"Gets a Server record by unique ID."
		id = int(id)
		try:
			result = self._prodserver.GetServerById(id=id)
		except FaultException, e:
			_handleFaultException(e)
		return _getServerFromNode(result['server'])


	# Builds

	def getBuilds(self, product='', version='', subproduct='', build='', platform='', language='', compiletarget='', licensing='',
		format='', certlevel='', status='', date='', metadata=''):
		"""
			get a list of Builds meeting specific criteria

			product        String  Name of a current product
			version        String  Name of a current version of the given product
			build          String  Name of a current build of the given product
			platform       String  Name of a current Platform in Codex
			language       String  Name of a current language in Codex
			compiletarget  String  Name of a valid compile target value
			licensing      String  Name of a valid licensing value
			format         String  Name of a valid format value
			certlevel      String  Name of a valid Certification Level
			status         String  Name of a valid status
			date           String  A date to filter by, of the form YYYY/MM/DD or YYYY/MM/DD:HH:MM:SS (same as Perforce)
			metadata       String  A set of key/value pairs concatenated together "key1=value1:key2=value2"

		This is the most complex method in the API aside from postBuild. This is
			the primary method for querying Codex for a set of builds with an arbitrary
			set of parameters. As such, each parameter accepts a variety of values:

	1.	A fixed value.
			The method will search the database for an exact match.
	2.	A wildcarded value.
			The parameters that are passed textual strings can be given wildcard characters
			(asterisk) at the beginning and/or end of the string. So, a product value of 
			"Photo*" will search for any product starting with "Photo". The same call without
			the asterisk will match only the "Photo" product. Parameters that accept asterisk
			wildcards are: Product, Version, build, and language. Passing just an asterisk 
			as a parameter value is not allowed.
	3.	Inequality values.
			Parameters whose values represent part of an ordered range can accept =, >, <, >=,
			and <= values as prefixes to the string value (i.e. ">Not Tested" as a certlevel 
			value). Specifying = as a prefix means the query will match only that value. The
			parameters that accept inequality prefixes are:
				CertLevel - Accepts all inequality values. If no inequality prefix is given 
					default behaviour is >= (selecting builds that have a certlevel greater than
					or equal to the given value)
				Date - Accepts all inequality values. If no inequality prefix is given, default 
					behaviour is <= (selecting builds that have a date on or before the given value.)
	4.	No value.
			If a parameter is left blank (passed as an empty string), then it will not
			be used as a filter, and builds can be returned matching any value for that parameter.

		"""
		try:
			result = self._prodserver.GetBuilds(
				productname  =  product,
				versionname = version,
				subproductname = subproduct,
				buildname = build,
				platformname = platform,
				languagecode = language,
				compilertargetname = compiletarget,
				licensemodelname = licensing,
				formatname = format,
				certlevel = certlevel,
				statusname = status,
				date = date)
		except FaultException, e:
			_handleFaultException(e)
		return _getBuildListFromNode(result['buildlist'])
		

	def getBuildsByLocation(self, protocol='', server='', path='', query=''):
		"""
			get a list of Builds posted to a particular location
			
			protocol   String   Protocol to search for 'afp' 'ftp' 'smp' 'p4'
			server     String   whole or partial server name to filter by
			path       String   full or partial path to filter by
			query      String   query value to filter by

		The server and path parameters accept wildcarded values, meaning they can be given wildcard
			characters (asterisk) at the beginning and/or end of the string. So, a server value of 
			"hermes*" will search for any server starting with "hermes". The same call without the 
			asterisk will match only the "hermes" server (and not "hermes.corp.adobe.com"). Passing
			just an asterisk as a parameter value is not allowed.

			If a parameter is left blank (passed as an empty string), then it will not be used as a 
			filter, and builds can be returned matching any value for that parameter.
		"""
		try:
			result = self._prodserver.GetBuildsByLocation(protocol=protocol, servername=server, path=path, query=query)
		except FaultException, e:
			_handleFaultException(e)
		return _getBuildListFromNode(result['buildlist'])
		

	def getBuildsFromProfile(self, product, version, profile, componentproduct, componentsubproduct, platform, language):
		"""
			get a list of Builds based on the contents of a profile
			
		The parameters accept wildcarded values, meaning they can be given wildcard characters
			(asterisk) at the beginning and/or end of the string. Passing just an asterisk as a 
			parameter value is not allowed.
		If a parameter is left blank (passed as an empty string), then it will not be used as
			a filter, and builds can be returned matching any value for that parameter.
		"""
		try:
			result = self._prodserver.GetBuildsFromProfile(productname=product, versionname=version, profilename=profile,
				component=componentproduct, subproductname=componentsubproduct, platformname=platform, languagecode=language)
		except FaultException, e:
			_handleFaultException(e)

		return _getBuildListFromNode(result['buildlist'])


	def getBuildsFromProfileWithComponent(self, product, version, profile, componentproduct, componentsubproduct, platform, language, filtercomponent, filterbuild):
		"""
			get a list of Builds based on the contents of a profile
			
		The parameters accept wildcarded values, meaning they can be given wildcard characters
			(asterisk) at the beginning and/or end of the string. Passing just an asterisk as a 
			parameter value is not allowed.
		If a parameter is left blank (passed as an empty string), then it will not be used as
			a filter, and builds can be returned matching any value for that parameter.
		"""
		try:
			result = self._prodserver.GetBuildsFromProfileWithComponent(productname=product, versionname=version, profilename=profile,
				component=componentproduct, subproductname=componentsubproduct, platformname=platform, languagecode=language,
				filtercomponent=filtercomponent, buildname=filterbuild)
		except FaultException, e:
			_handleFaultException(e)

		return _getBuildListFromNode(result['buildlist'])


	def getBuildFromProfile(self, product, version, profile, componentproduct, componentsubproduct, platform, language):
		"""
			get a build based on the contents of a profile
			
		The parameters accept wildcarded values, meaning they can be given wildcard characters
			(asterisk) at the beginning and/or end of the string. Passing just an asterisk as a 
			parameter value is not allowed.
		If a parameter is left blank (passed as an empty string), then it will not be used as
			a filter, and builds can be returned matching any value for that parameter.
		"""
		try:
			result = self._prodserver.GetBuildFromProfile(productname=product, versionname=version, profilename=profile,
				component=componentproduct, subproductname=componentsubproduct, platformname=platform, languagecode=language)
		except FaultException, e:
			_handleFaultException(e)

		return _getBuildFromNode(result['build'])
		
	def getAllBuildsFromProfile(self, product, version, profile, platform, language):
		"get a list of all Builds in a profile, not filtered by comoponent"
		try:
			result = self._prodserver.GetAllBuildsFromProfile(productname=product, versionname=version, profilename=profile,
				platformname=platform, languagecode=language)
		except FaultException, e:
			_handleFaultException(e)
		return _getBuildListFromNode(result['buildlist'])

	def getBuildComponents(self, id):
		"returns a list of Builds used by the build having the passed in id"
		id = int(id)
		try:
			result = self._prodserver.GetBuildComponents(id=id)
		except FaultException, e:
			_handleFaultException(e)
		return _getBuildListFromNode(result['buildlist'])
		
	def getBuildsUsing(self, id):
		"returns a list of Builds using the build having the passed in id"
		id = int(id)
		try:
			result = self._prodserver.GetBuildsUsing(id=id)
		except FaultException, e:
			_handleFaultException(e)
		return _getBuildListFromNode(result['buildlist'])


	def getBuildByID(self, id):
		"get a specific Build by id"
		id = int(id)
		try:
			result = self._prodserver.GetBuildById(buildid=id)
		except FaultException, e:
			_handleFaultException(e)
		return _getBuildFromNode(result['build'])

	def addBuild(self, manifestFile, URI, certlevel, status, username, password):
		"""
			add a new build to codex; returns the id of the new build
		
			pass the contents of the manifest.xml file as manifestFile
		"""
		try:
			result = self._prodserver.AddBuild(manifestfile=manifestFile,uri=URI,certlevel=certlevel,
				statusname=status, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['id']
			
	def addNote(self, id, text, username, password):
		"add a note to a build (specified by id), returns the updated Build"
		id = int(id)
		try:
			result = self._prodserver.AddNote(buildid=id, notetext=text, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return _getBuildFromNode(result['build'])

	def setCertLevel(self, id, certlevel, username, password):
		"set the certification level of the build having a given id; returns the updated Build"
		id = int(id)
		try:
			result = self._prodserver.SetCertLevel(id=id, certlevel=certlevel, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return _getBuildFromNode(result['build'])

	def setStatus(self, id, status, username, password):
		"set the status of the build having a given id; returns the updated Build"
		id = int(id)
		try:
			result = self._prodserver.SetStatus(id=id, statusname=status, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return _getBuildFromNode(result['build'])

	def setLocation(self, id, URI, username, password):
		"set the uri of the build having a given id; returns the updated Build"
		id = int(id)
		try:
			result = self._prodserver.SetLocation(id=id, uri=URI, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return _getBuildFromNode(result['build'])

	def setMetadata(self, id, key, value, username, password):
		"sets a key value pair in the build having a given id; returns the updated Build"
		id = int(id)
		try:
			result = self._prodserver.SetMetadata(id=id, key=key, value=value, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return _getBuildFromNode(result['build'])

	def addMetadata(self, id, key, value, username, password):
		"sets a key value pair in the build having a given id; returns the updated Build"
		id = int(id)
		try:
			result = self._prodserver.AddMetadata(id=id, key=key, value=value, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return _getBuildFromNode(result['build'])

	def getMetadataKeys(self, product, version):
		"Gets the list of metadata keys that have been defined in Codex for the given Product/Version"
		try:
			result = self._prodserver.GetMetadataKeys(product=product, version=version)
		except FaultException, e:
			_handleFaultException(e)
		return _getMetadataKeyListFromNode(result['metadatakeylist'])

	def addMetadataKey(self, product, version, key, username, password):
		"Adds a new metadata key to Codex for the optionally given product/version. The new key is then available for any build for the given product and version."
		id = int(id)
		try:
			result = self._prodserver.AddMetadataKey(key=key, productname=product, versionname=version, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['id']

	def deleteBuild(self, id, username, password):
		"deletes a build from codex by id; returns boolean indicating success"
		id = int(id)
		try:
			result = self._prodserver.DeleteBuild(id=id, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['operationresult']
		


	# Profiles

	def getProfiles(self, product, version):
		"Returns a list of ProfileData (metadata) records"
		try:
			result = self._prodserver.GetProfiles(productname=product, versionname=version)
		except FaultException, e:
			_handleFaultException(e)
		return _getProfileDataListFromNode(result['profiledatalist'])

	def getProfilesAndRecords(self, product, version):
		"Returns a list of Profiles (metadata) records"
		try:
			result = self._prodserver.GetProfilesAndRecords(productname=product, versionname=version)
		except FaultException, e:
			_handleFaultException(e)
		return _getProfileListFromNode(result['profilelist'])

	def getProfileByName(self, product, version, name):
		"returns the requested Profile object"
		try:
			result = self._prodserver.GetProfileByName(profilename=name, productname=product, versionname=version)
		except FaultException, e:
			_handleFaultException(e)
		return _getProfileFromNode(result['profile'])

	def getProfileByID(self, id):
		"returns the Profile object requested by id"
		id = int(id)
		try:
			result = self._prodserver.GetProfileById(profileid=id)
		except FaultException, e:
			_handleFaultException(e)
		return _getProfileFromNode(result['profile'])

	def addProfile(self, product, version, name, username, password):
		"add a profile; returns the profile id"
		try:
			result = self._prodserver.AddProfile(productname=product, versionname=version, profilename=name, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['profileid']

	def setProfileParent(self, id, product, version, username, password):
		"set the parent product of a profile given by id; returns the updated Profile"
		id = int(id)
		try:
			result = self._prodserver.SetProfileParent(id=id, productname=product, versionname=version, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return _getProfileFromNode(result['profile'])

	def setProfileDescription(self, id, description, username, password):
		"set the description of a profile given by id; returns the updated Profile"
		id = int(id)
		try:
			result = self._prodserver.SetProfileDescription(id=id, description=description, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return _getProfileFromNode(result['profile'])

	def setProfileName(self, id, name, username, password):
		"set the name of a profile given by id; returns the updated Profile"
		id = int(id)
		try:
			result = self._prodserver.SetProfileName(id=id, name=name, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return _getProfileFromNode(result['profile'])

	def deleteProfile(self, id, username, password):
		"delete a profile by id; returns boolean indicating success"
		id = int(id)
		try:
			result = self._prodserver.DeleteProfile(id=id, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['operationresult']

	def cloneProfile(self, id, product, version, name, username, password):
		"add a profile using the one specified by id as a template; returns the profile id"
		id=int(id)
		try:
			result = self._prodserver.CloneProfile(profileid=id, productname=product, versionname=version, profilename=name, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['profileid']


	# Profile Record

	def getProfileRecordByName(self, id, product, subproduct):
		"fetch a ProfileRecord by profile id and product name"
		try:
			result = self._prodserver.GetProfilerecordByName(productname=product, subproductname=subproduct, profileid=id)
		except FaultException, e:
			_handleFaultException(e)
		return _getProfileRecordFromNode(result['profilerecord'])

	def addProfileRecord(self, id, product, version, subproduct, username, password):
		"add a profilerecord to the profile specified by id for the given product version; returns record id"
		id=int(id)
		try:
			result = self._prodserver.AddProfilerecord(productname=product, versionname=version, subproductname=subproduct, profileid=id, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['id']

	def setProfileRecordToLatest(self, id, certlevel, compilertarget, licensing, format, username, password):
		"sets a profilerecord given by id to reference the latest build having specified settings; returns ?? id"
		id=int(id)
		try:
			result = self._prodserver.SetProfilerecordToLatest(productname=product, profilerecordid=id, 
				certlevel=certlevel, compilertargetname=compilertarget, licensemodelname=licensing,
				formatname=format, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['id']

	def setProfileRecordToBuild(self, id, build, compilertarget, licensing, format, username, password):
		"sets a profilerecord given by id to reference a specfic build; returns ?? id"
		id=int(id)
		try:
			result = self._prodserver.SetProfilerecordToBuild(profilerecordid=id, buildname=build, 
				compilertargetname=compilertarget, licensemodelname=licensing, formatname=format, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['id']

	def setProfileRecordToDefault(self, id, profile, username, password):
		"sets a profilerecord given by id to reference another profile; returns ?? id"
		id=int(id)
		try:
			result = self._prodserver.SetProfilerecordToDefault(id=id, profilename=profile, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['id']

	def deleteProfileRecord(self, id, username, password):
		"delete a profile record by id; return boolean indicating success"
		id = int(id)
		try:
			result = self._prodserver.DeleteProfileRecord(id=id, ldapcredentials={'userid':username, 'password':password})
		except FaultException, e:
			_handleFaultException(e)
		return result['operationresult']



	def queryDependencyComponent(self, product, version, platform, component, language):
		return self._prodserver.QueryDependencyComponent(parentproduct=product, versionname=version, platform=platform, component=component, language=language)

#
# helper functions
#

def _handleFaultException(exception):
	"takes a ZSI.FaultException and reraises a more specific type of exception if possible, based on the string"
	s = exception.__str__()
	if 'does not exist' in s: raise KeyError, s
	elif 'No entity found for query' in s: raise KeyError, s
	elif 'already exists' in s: raise NameError, s
	elif 'InvalidNameException' in s: raise NameError, s
	else: raise FaultException, s

def _addOptionalAttributes(attributeDictionary, keylist):
	"takes a dictionary and adds null strings as values for any missing keys"
	for key in keylist:
		if not attributeDictionary.has_key(key):
			attributeDictionary[key]=''

def _getProductListFromNode(node):
	'returns a list of Products when passed an xml node representing a productlist'
	try:	
		productNodes = node['product']
	except KeyError:
		productNodes = []
	productList = []
	for productNode in productNodes:
		productList.append(_getProductFromNode(productNode))
	return productList

def _getProductFromNode(node):
	'returns a Product when passed an xml node representing a product'
	attrs = node['_attrs']
	return datatypes.Product(attrs['name'], attrs['type'], attrs['id'], node['link'], node['description'])

def _getSubproductListFromNode(node):
	'returns a list of Subproducts when passed an xml node representing a subproductlist'
	try:	
		childNodes = node['subproduct']
	except KeyError:
		childNodes = []
	resultList = []
	for child in childNodes:
		resultList.append(_getSubproductFromNode(child))
	return resultList

def _getSubproductFromNode(node):
	'returns a Subroduct when passed an xml node representing a product'
	attrs = node['_attrs']
	return datatypes.Subproduct(attrs['id'], attrs['name'], node['description'])

def _getVersionListFromNode(node):
	'return a list of Versions when passed an xml node representing a versionlist'
	try:
		versionNodes = node['version']
	except KeyError:
		versionNodes = []
	versionList = []
	for versionNode in versionNodes:
		versionList.append(_getVersionFromNode(versionNode))
	return versionList

def _getVersionFromNode(node):
	'return a Version when passed an xml node representing a version'
	attrs = node['_attrs']
	#optional attributes
	_addOptionalAttributes(attrs, ['codename', 'unified_id'])
	return datatypes.Version(attrs['product'], attrs['name'], attrs['codename'], attrs['id'], attrs['unified_id'],
		node['link'], node['description'])

def _getCertLevelListFromNode(node):
	'return a list of CertLevels when passed an xml node representing a certificationlevellist'
	resultlist = []
	try:	
		childNodes = node['certificationlevel']
	except KeyError:
		childNodes = []
	for child in childNodes:
		resultlist.append(_getCertLevelFromNode(child))
	return resultlist

def _getCertLevelFromNode(node):
	'return a CertLevel when passed an xml node representing a version'
	attrs = node['_attrs']
	#optional attributes
	_addOptionalAttributes(attrs, ['color'])
	return datatypes.CertLevel(attrs['name'], attrs['id'], attrs['color'])

def _getStatusListFromNode(node):
	'return a list of Statuses when passed an xml node representing a statuslist'
	resultlist = []
	try:	
		childNodes = node['status']
	except KeyError:
		childNodes = []
	for child in childNodes:
		resultlist.append(_getStatusFromNode(child))
	return resultlist

def _getStatusFromNode(node):
	'return a Status when passed an xml node representing a status'
	attrs = node['_attrs']
	return datatypes.Status(attrs['name'], attrs['id'], attrs['isavailable'])

def _getCompilerTargetListFromNode(node):
	'return a list of CompilerTargets when passed an xml node representing a compilertargetlist'
	resultlist = []
	try:	
		childNodes = node['compilertarget']
	except KeyError:
		childNodes = []
	for child in childNodes:
		resultlist.append(_getCompilerTargetFromNode(child))
	return resultlist

def _getCompilerTargetFromNode(node):
	'return a CompilerTarget when passed an xml node representing a compilertarget'
	attrs = node['_attrs']
	return datatypes.CompilerTarget(attrs['name'], attrs['id'])

def _getLicenseModelListFromNode(node):
	'return a list of LicenseModels when passed an xml node representing a licensemodellist'
	resultlist = []
	try:	
		childNodes = node['licensemodel']
	except KeyError:
		childNodes = []
	for child in childNodes:
		resultlist.append(_getLicenseModelFromNode(child))
	return resultlist

def _getLicenseModelFromNode(node):
	'return a LicenseModel when passed an xml node representing a licensemodel'
	attrs = node['_attrs']
	return datatypes.LicenseModel(attrs['name'], attrs['id'])

def _getFormatListFromNode(node):
	'return a list of Formats when passed an xml node representing a formatlist'
	resultlist = []
	try:	
		childNodes = node['format']
	except KeyError:
		childNodes = []
	for child in childNodes:
		resultlist.append(_getFormatFromNode(child))
	return resultlist

def _getFormatFromNode(node):
	'return a Format when passed an xml node representing a format'
	attrs = node['_attrs']
	return datatypes.Format(attrs['name'], attrs['id'])

def _getPlatformListFromNode(node):
	'return a list of Platforms when passed an xml node representing a platformlist'
	resultlist = []
	try:	
		childNodes = node['platform']
	except KeyError:
		childNodes = []
	for child in childNodes:
		resultlist.append(_getPlatformFromNode(child))
	return resultlist

def _getPlatformFromNode(node):
	'return a Platform when passed an xml node representing a platform'
	attrs = node['_attrs']
	#optional attributes
	_addOptionalAttributes(attrs, ['description'])
	return datatypes.Platform(attrs['name'], attrs['id'], attrs['description'])

def _getServerListFromNode(node):
	'return a list of Servers when passed an xml node representing a serverlist'
	resultlist = []
	try:	
		childNodes = node['server']
	except KeyError:
		childNodes = []
	for child in childNodes:
		resultlist.append(_getServerFromNode(child))
	return resultlist

def _getServerFromNode(node):
	'return a Server when passed an xml node representing a server'
	attrs = node['_attrs']
	return datatypes.Server(attrs['name'], attrs['id'], attrs.get('webname', None))

def _getLanguageListFromNode(node):
	'return a list of Languages when passed an xml node representing a languagelist'
	resultlist = []
	try:	
		childNodes = node['language']
	except KeyError:
		childNodes = []
	for child in childNodes:
		resultlist.append(_getLanguageFromNode(child))
	return resultlist

def _getLanguageFromNode(node):
	'return a Language when passed an xml node representing a language'
	attrs = node['_attrs']
	#optional attributes
	_addOptionalAttributes(attrs, ['code'])
	return datatypes.Language(attrs['name'], attrs['id'], attrs['code'])

def _getProductTypeListFromNode(node):
	'return a list of ProductTypes when passed an xml node representing a producttypelist'
	resultlist = []
	try:	
		childNodes = node['producttype']
	except KeyError:
		childNodes = []
	for child in childNodes:
		resultlist.append(_getProductTypeFromNode(child))
	return resultlist

def _getProductTypeFromNode(node):
	'return a ProductTypes when passed an xml node representing a producttype'
	attrs = node['_attrs']
	return datatypes.ProductType(attrs['id'], attrs['name'], attrs['description'])

def _getPickupOptionListFromNode(node):
	'return a list of PickupOptions when passed an xml node representing a pickupoptionlist'
	resultlist = []
	try:	
		childNodes = node['pickupoption']
	except KeyError:
		childNodes = []
	for child in childNodes:
		resultlist.append(_getPickupOptionFromNode(child))
	return resultlist

def _getPickupOptionFromNode(node):
	'return a ProductTypes when passed an xml node representing a pickupoption'
	attrs = node['_attrs']
	return datatypes.PickupOption(attrs['id'], attrs['name'])

def _getBuildListFromNode(node):
	'return a list of Builds when passed an xml node representing a buildlist'
	resultlist = []
	try:	
		childNodes = node.get('build', ())
	except KeyError:
		childNodes = []
	for child in childNodes:
		resultlist.append(_getBuildFromNode(child))
	return resultlist

def _getBuildFromNode(node):
	'return a Build when passed an xml node representing a build'
	attrs = node['_attrs']
	result = datatypes.Build(attrs['id'], attrs['product'], attrs['version'], attrs['subproduct'], attrs.get('build', None), attrs['platform'],
		attrs['language'], attrs['compilertarget'], attrs['licensemodel'], attrs.get('format', None), attrs['certlevel'],
		attrs.get('status', None), attrs.get('date', None))
	# process sources
	sources = node.get('sources', {}).get('source', ())
	for source in sources:
		source_attrs = source['_attrs']
		# optional source attributes
		_addOptionalAttributes (source_attrs, ['path','protocol','query','server'])
		result.addSource(source_attrs['protocol'], source_attrs['server'], source_attrs['path'], source_attrs['query'])
	# process location
	location = node.get('location', None)
        if location:
		loc_attrs = location['_attrs']
		# optional location attributes
		_addOptionalAttributes(loc_attrs, ['path','protocol','query','server'])
		result.addLocation(loc_attrs['protocol'], loc_attrs['server'], loc_attrs['path'], loc_attrs['query'])
	# process notes
	notes = node.get('notes', {}).get('note', ())
	for note in notes:
		note_attrs = note['_attrs']
		# optional note attributes
		_addOptionalAttributes(note_attrs, ['id'])
		result.addNote(note_attrs['id'], note['_text'])
	# process metadata
	metadata = node.get('metadata', {}).get('item', ())
	for datum in metadata:
		datum_attrs = datum['_attrs']
		# optional metadata attributes
		_addOptionalAttributes(datum_attrs, ['id','key','value'])
		result.addMetadata(datum_attrs['id'], datum_attrs['key'], datum_attrs['value'])
	return result

def _getProfileDataListFromNode(node):
	'return a list of ProfileData objects when passed an xml node representing a profiledatalist'
	resultlist = []
	try:	
		childNodes = node['profiledata']
	except KeyError:
		childNodes = []
	for child in childNodes:
		resultlist.append(_getProfileDataFromNode(child))
	return resultlist

def _getProfileDataFromNode(node):
	'return a ProfileData object when passed an xml node representing profiledata'
	attrs = node['_attrs']
	#optional attributes
	_addOptionalAttributes(attrs, ['description','parentproduct','parentversion','product','version'])
	return datatypes.ProfileData(attrs['name'], attrs['product'], attrs['version'], attrs['id'], attrs['description'],
		attrs['parentproduct'], attrs['parentversion'])

def _getProfileListFromNode(node):
	'return a list of Profile objects when passed an xml node representing a profilelist'
	resultlist = []
	try:	
		childNodes = node['profile']
	except KeyError:
		childNodes = []
	for child in childNodes:
		resultlist.append(_getProfileFromNode(child))
	return resultlist

def _getProfileFromNode(node):
	'return a Profile object when passed an xml node representing profile'
	attrs = node['_attrs']
	#optional attributes
	_addOptionalAttributes(attrs, ['description','parentproduct','parentversion','product','version'])
	# get the profilerecords from this profile
	profileRecordsList = []
	for child in node.get('profilerecords', {}).get('profilerecord', ()):
		profileRecordsList.append(_getProfileRecordFromNode(child))
	return datatypes.Profile(attrs['name'], attrs['product'], attrs['version'], attrs['id'], attrs['description'],
		attrs['parentproduct'], attrs['parentversion'], profileRecordsList)

def _getProfileRecordFromNode(node):
	'return a ProfileRecord when passed an xml node representing a profilerecord'
	attrs = node['_attrs']
	#optional attributes
	_addOptionalAttributes(attrs, ['certlevel','compiletarget','format','licensemodel','parentprofile','pickupoption'])
	return datatypes.ProfileRecord(attrs['id'], attrs['profileid'], attrs['product'], attrs['version'], attrs['subproduct'], 
		attrs['pickupoption'], attrs['certlevel'], attrs['compiletarget'], attrs['licensemodel'], attrs['format'],
		attrs['build'], attrs['parentprofile'])

def _getMetadataKeyListFromNode(node):
	'return a list of MetadataKeys when passed an xml node representing a list of MetadataKey'
	resultlist = []
	try:	
		childNodes = node['metadatakey']
	except KeyError:
		childNodes = []
	for child in childNodes:
		resultlist.append(_getMetadataKeyFromNode(child))
	return resultlist

def _getMetadataKeyFromNode(node):
	'return a MetadataKey when passed an xml node representing a metadata key-value pair'
	attrs = node['_attrs']
	#optional attributes
	_addOptionalAttributes(attrs, ['product','version'])
	return datatypes.MetadataKey(node['key'], node['id'], attrs['product'], attrs['version'])

def _getPlatformGroupListFromNode(node):
	'return a list of PlatformGroups when passed an xml node representing a platformgrouplist'
	resultlist = []
	try:	
		childNodes = node['platformgroup']
	except KeyError:
		childNodes = []
	for child in childNodes:
		resultlist.append(_getPlatformGroupFromNode(child))
	return resultlist

def _getPlatformGroupFromNode(node):
	'return a PlatformGroup when passed an xml node representing a platformgroup'
	attrs = node['_attrs']
	# get the platformgrouprecords from this profile
	platformgroupRecordsList = []
	for child in node.get('platformgrouprecordlist', {}).get('platformgrouprecord', ()):
		platformgroupRecordsList.append(_getPlatformgroupRecordFromNode(child))
	return datatypes.PlatformGroup(attrs['name'], attrs['id'], attrs['product'], attrs['version'], platformgroupRecordsList)

def _getPlatformgroupRecordFromNode(node):
	'return a PlatformGroupRecord when passed an xml node representing a platformgrouprecord'
	attrs = node['_attrs']
	return datatypes.PlatformGroupRecord(attrs['recordid'], attrs['groupid'], attrs['platform'])

def _getContactListFromNode(node):
	'return a list of Contacts when passed an xml node representing a contactlist'
	resultlist = []
	try:	
		childNodes = node['contact']
	except KeyError:
		childNodes = []
	for child in childNodes:
		resultlist.append(_getContactFromNode(child))
	return resultlist

def _getContactFromNode(node):
	'return a Contact when passed an xml node representing a contact'
	attrs = node['_attrs']
	return datatypes.Contact(attrs['name'], attrs['id'], attrs['type'])

def _getContactTypeListFromNode(node):
	'return a list of ContactTypes when passed an xml node representing a contacttypelist'
	resultlist = []
	try:	
		childNodes = node['contacttype']
	except KeyError:
		childNodes = []
	for child in childNodes:
		resultlist.append(_getContactTypeFromNode(child))
	return resultlist

def _getContactTypeFromNode(node):
	'return a Contact when passed an xml node representing a contact'
	attrs = node['_attrs']
	return datatypes.ContactType(attrs['name'], attrs['id'])


#
# self-test functions
#

def printProducts():
	"""
		calls getProducts() and formats the response
	"""
	result = codex.getProducts()
	for res in result:
           print res._name, res._type, res._id, res._link, res._description

def printProduct(result):
	"""
		prints the result of getProductByName or getProductByID
	"""

	print "Name: %s (ID: %d)" % (result._name, result._id)
	print "Type: %s" % (result._type)
	print "Link: %s" % (result._link)
	print "Description: %s" % (result._description)


def printBuildId(result):
	"""
		Prints out just a build id from functions that return it
	"""
	print "%d" % (result['buildid'])


if __name__ == "__main__":

	# These lines need to be done for all the examples below

        if len(sys.argv) > 1:
           tracefile = sys.argv[1]
           trace = open(tracefile, "w")
           tracer = 1
        else:
           trace = None
           tracer = 0

	# instantiate the class
	codex = CodexService(trace)
	printProducts()
	"""
        manifest = open("codex1.xml").read()
        uri = "ftp://hermes.corp.adobe.com/Photoshop/10.0/blah/blah/blah"
        certlevel = "Not Tested"
        status = "Available"
        username = ""
        password = ""
	"""


	#result = codex.addBuild(manifest, uri, certlevel, status, username, password)
        #print result

	#result = codex.getBuildFromProfile("Photoshop", "10.0", "Default", "Adobe Help Viewer", "Default", "win32", "en_US")
	#printProducts()
	#printProduct(codex.getProductByName("GoogleMaps"))
	#printProduct(codex.getProductByID(11))
	#printBuildId(codex.queryDependencyComponent("Photoshop", "10.0", "osx10", "Bridge", "en_US"))

        if tracer:
           trace.close()

	sys.exit()

