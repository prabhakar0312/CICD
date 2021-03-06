import json
import sys
import subprocess
import re
import xml.etree.ElementTree as ET

def readFile(filename):
	file = open(filename)
	file_text = file.read()
	file.close()
	return file_text

admin_accesstoken = 'eca716de14ec2de174ffcbb8709b4b2dafa62b92701ce302a64c1d84020e6714'
filename = sys.argv[1]
policy_filename = sys.argv[2]
method_filename = sys.argv[3]
mapping_rules_filename = sys.argv[4]
activedocs_filename = sys.argv[5]
application_plan_filename = sys.argv[6]

product_deploy_config=json.loads(readFile(filename))
policy_config=json.loads(readFile(policy_filename))
policy_config=json.dumps(policy_config) 
method_config=json.loads(readFile(method_filename))
mapping_rules_config=json.loads(readFile(mapping_rules_filename))
activedocs_config=json.loads(readFile(activedocs_filename))
activedocs_config_spec=json.dumps(activedocs_config["body"]) 
application_plan_config=json.loads(readFile(application_plan_filename))

admin_url = '3scale-admin.apps.api.abgapiservices.com'

remote_name = 'abg-cicd'

add_remote_cmd = '3scale -k remote add abg-cicd https://' + admin_accesstoken + '@' +product_deploy_config["admin_url"]
add_remote = subprocess.check_output(add_remote_cmd, shell=True, universal_newlines=True)

#Create API Product
apply_product_cmd = '3scale -k service apply ' + remote_name + ' ' + product_deploy_config["product_name"] + \
									' -a oidc -n ' + product_deploy_config["product_name"]
apply_product = subprocess.check_output(apply_product_cmd, shell=True, universal_newlines=True)
service_id = apply_product.split(":")[1].strip()
print "Product Created =>" + service_id

#Apply API Product - Proxy Configuration
product_proxy_cmd = 'curl -k -s -X PATCH "https://' + admin_url + \
										'/admin/api/services/' + service_id + '/proxy.xml"' + \
										' -d \'access_token=' + admin_accesstoken + '\'' + \
							      ' --data-urlencode \'oidc_issuer_endpoint=' + product_deploy_config["oidc_endpoint"] + '\'' + \
							      ' --data-urlencode \'sandbox_endpoint=' + product_deploy_config["sandbox_endpoint"] + '\'' + \
							      ' --data-urlencode \'endpoint=' + product_deploy_config["endpoint"] + '\'' + \
                                  ' --data-urlencode \'api_backend=' + product_deploy_config["api_backend"] + '\'' + \
                                  ' -d \'api_test_path=' + product_deploy_config["api_test_path"] + '\'' + \
                                  ' -d \'oidc_issuer_type=' + "keycloak" + '\''
                                  
product_proxy = subprocess.check_output(product_proxy_cmd, shell=True, universal_newlines=True)
print "Product Proxy Configuration Updated  =>" + service_id

#Apply Product Policies

product_policy_cmd = 'curl -k -s -X PUT "https://' + admin_url + \
									'/admin/api/services/' + service_id + '/proxy/policies.json"' + \
									' -d \'access_token=' + admin_accesstoken + '\'' + \
									' --data-urlencode \'policies_config=' + policy_config + '\''

product_policy= subprocess.check_output(product_policy_cmd, shell=True, universal_newlines=True)                                 
print "Product Gateway Policy Applied =>" + policy_config

#Get Product Metric_id
product_getmetricid_cmd = 'curl -k -s -X GET "https://' + admin_url + \
                                         '/admin/api/services/' + service_id + '/metrics.xml?' + 'access_token=' + admin_accesstoken +'"'
										 
product_getmetricid = subprocess.check_output(product_getmetricid_cmd, shell=True, universal_newlines=True)
xmlparsed = ET.fromstring(product_getmetricid)
metric_id = xmlparsed[0][0].text
print " metric id = " + metric_id

#Apply Product Method
product_method_cmd = 'curl -k -s -X POST "https://' + admin_url + \
                                    '/admin/api/services/' + service_id + '/metrics/' + metric_id + '/methods.xml"' + \
									' -d \'access_token=' + admin_accesstoken + '\'' + \
									' --data-urlencode \'friendly_name=' + method_config["method_name"] + '\'' + \
									' --data-urlencode \'unit=' + method_config["unit"] + '\'' + \
									' --data-urlencode \'system_name=' + method_config["system_name"] + '\'' + \
                                                                        ' --data-urlencode \'description=' + method_config["description"] + '\''

product_method = subprocess.check_output(product_method_cmd, shell=True, universal_newlines=True)                                 
					
									
#Apply Product Mapping Rules
product_Mapping_rule_cmd = 'curl -k -s -X POST "https://' + admin_url + \
                                          '/admin/api/services/' + service_id + '/proxy/mapping_rules.xml"' + \
										  ' -d \'access_token=' + admin_accesstoken + '\'' + \
										  ' --data-urlencode \'http_method=' + mapping_rules_config["http_method"] + '\'' + \
										  ' --data-urlencode \'pattern=' + mapping_rules_config["pattern"] + '\'' + \
										  ' --data-urlencode \'delta=' + mapping_rules_config["delta"] + '\'' + \
										  ' --data-urlencode \'metric_id=' +   metric_id + '\'' + \
										  ' --data-urlencode \'position=' + mapping_rules_config["position"] + '\'' + \
										  ' --data-urlencode \'last=' + mapping_rules_config["last"] + '\''
										  
product_Mapping_rule = subprocess.check_output(product_Mapping_rule_cmd, shell=True, universal_newlines=True)                                 


#Apply Product Active Docs
product_activedocs_cmd = 'curl -k -s -X POST "https://' + admin_url + \
                                    '/admin/api/active_docs.json"' + \
									' -d \'access_token=' + admin_accesstoken + '\'' + \
									' --data-urlencode \'name=' + activedocs_config["name"] + '\'' + \
									' --data-urlencode \'service_id=' + service_id + '\'' + \
									' --data-urlencode \'body=' + activedocs_config_spec + '\'' + \
									' --data-urlencode \'description=' + activedocs_config["description"] + '\'' + \
									' --data-urlencode \'system_name=' + activedocs_config["system_name"] + '\'' + \
									' --data-urlencode \'skip_swagger_validations=' + activedocs_config["skip_swagger_validations"] + '\'' 
									
product_activedocs = subprocess.check_output(product_activedocs_cmd, shell=True, universal_newlines=True)                                 
print "Product Active docs added "

#Apply Product Application plan
product_application_plan_cmd = 'curl -k -s -X POST "https://' + admin_url + \
                                        '/admin/api/services/' + service_id + '/application_plans.xml"' + \
										' -d \'access_token=' + admin_accesstoken + '\'' + \
										' --data-urlencode \'name=' + application_plan_config["name"] + '\'' + \
									    ' --data-urlencode \'state_event=' + application_plan_config["state_event"] + '\'' + \
									    ' --data-urlencode \'system_name=' + application_plan_config["system_name"] + '\''

product_application_plan = subprocess.check_output(product_application_plan_cmd, shell=True, universal_newlines=True)                                 
print "Product Gateway Application Plan added =>" 

#Promote to Staging
promote_staging_cmd= 'curl -k -s  -X POST "https://' + admin_url + \
					'/admin/api/services/' + str(service_id) + \
           '/proxy/deploy.xml?access_token=' + admin_accesstoken + '"';
promote_staging = subprocess.check_output(promote_staging_cmd, shell=True, universal_newlines=True)
print "Product Promoted to Staging =>" + promote_staging

#Get Version
get_version_cmd = 'curl -k -s  -X GET "https://' + admin_url + \
					'/admin/api/services/' + str(service_id) + \
           '/proxy/configs/sandbox/latest.json?access_token=' + admin_accesstoken + '"';
get_version = json.loads(subprocess.check_output(get_version_cmd, shell=True, universal_newlines=True))
version = get_version["proxy_config"]["version"]


#Promote to Production
promote_production_cmd= 'curl -k -s  -X POST "https://' + admin_url + \
					'/admin/api/services/' + str(service_id) + \
           '/proxy/configs/sandbox/' + str(version) + '/promote.json?access_token=' \
           + admin_accesstoken + '&to=production"';
promote_production = subprocess.check_output(promote_production_cmd, shell=True, universal_newlines=True)

print "Product Promoted to Production =>"
