# Configuration file for paths and other constants

# Base directories
BASE_RELEASE_DIR = 'release'
BASE_TEMPLATE_PATH = '/app/file_templates'#'./src/file_templates' 
BASE_RELEASE_DB = ['datatrak_bgt_agt','datatrak_bgt_awb']

# Version paths
VERSION_PATHS = {
    'agt': './datatrak_bgt_agt/version.txt',
    'awb': './datatrak_bgt_awb/version.txt'
}

# Release filenames
RELEASE_FILES = [
    '1_datatrak_create_new_table_scripts.sql',
    '2_datatrak_alter_table_scripts.sql',
    '3_datatrak_functions_scripts.sql',
    '4_datatrak_triggers_scripts.sql',
    '5_datatrak_views_scripts.sql',
    '6_datatrak_sp_scripts.sql',
    '7_new_datatrak_data_insertion_scripts.sql',
]

# Permission and version filenames
RELEASE_TEMPLATE_FILES = [
    '__DO_IT.bat_txt',
    'scriptlist.txt',
    '8_permission_datatrak_scripts.sql',
    '9_new_datatrak_mis_version_update_scripts.sql'
]

RELEASE_FILE_MAPPING = {
    'tables': '1_datatrak_create_new_table_scripts.sql',
    'alter_table':'2_datatrak_alter_table_scripts.sql',
    'index':'2_datatrak_alter_table_scripts.sql',    
    'functions': '3_datatrak_functions_scripts.sql',
    'triggers':'4_datatrak_triggers_scripts.sql', 
    'views':'5_datatrak_views_scripts.sql',
    'stored_procedures': '6_datatrak_sp_scripts.sql',      
    'insert_statements':'7_new_datatrak_data_insertion_scripts.sql'
}
 
# Default header template
DEFAULT_HEADER_FILE = 'default_header.txt'
DEFAULT_HEADER_FILE_WITH_CREATE = 'defalt_header_with_create.txt'

RELEASE_DOCX = 'BGT MsSQL DBs Release Deployment Guide.docx'