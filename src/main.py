import logging
import sys
import os
import config
from bgt_release_handler import BGTReleaseHandler

# Set up logging configuration to log INFO and higher levels to both console and a file
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),                       # Log to console
        logging.FileHandler('bgt_release_handler.log', mode='w')      # 'w' mode to overwrite file on each run
    ]
)
logger = logging.getLogger(__name__)

def main(files_changed_with_tags, release_number):
    """
    Main function to create release directories, generate release files, and copy the input files to the release files.
    """
    # Initialize object for BGTReleaseHandler  
    release_handler = BGTReleaseHandler(
            files_changed_with_tags=files_changed_with_tags, 
            release_number=release_number
        )
    try:
        # Initialize variables with default values
        agt_file_data, awb_file_data = None, None
        
        # Check if version information is provided in the input
        if not release_handler.check_version_in_input():
            agt_file_data, awb_file_data = release_handler.get_versions_file_data(version_file_paths=config.VERSION_PATHS)
            
            # Raise error if both data files are missing
            if not agt_file_data and not awb_file_data:
                raise ValueError("Both AGT and AWB version data files are missing.")
        
        logger.info(f"Initializing version manager with AGT:{agt_file_data} and AWB:{awb_file_data} file data.")    
        release_handler.initialize_version_manager(agt_file_data=agt_file_data, awb_file_data=awb_file_data)
        
        # Retrieve database versions
        db_versions_dict = release_handler.get_db_versions()
        if not db_versions_dict:
            raise ValueError("No database versions found.")
        
        logger.info("Setting database versions in the release handler.")
        release_handler.set_db_versions_dict(db_versions_dict=db_versions_dict)
        
        # Generate release file path for AWB and AGT
        awb_agt_release_file_path = release_handler.generate_awb_agt_release_file_path(release_dir_name=config.BASE_RELEASE_DIR)
        if not awb_agt_release_file_path:
            raise ValueError("Failed to create release file path for AWB and AGT.")
        
        logger.info("Initializing release path and resource manager.")
        release_handler.initialize_release_path_and_resource_manager(awb_agt_release_file_path=awb_agt_release_file_path)
        
        # Create release directories
        logger.info("Creating release directories with database names.")
        release_dirs_with_db_name = release_handler.create_empty_release_directories(release_db_dir_names=config.BASE_RELEASE_DB)
        if not release_dirs_with_db_name:
            raise ValueError("Failed to create release directories for databases.")
        
        logger.info("Setting release directories with database names.")
        release_handler.set_release_dirs_with_db_name(release_dirs_with_db_name=release_dirs_with_db_name)

        # Create bash permission files for the release
        logger.info("Creating release bash permission files.")
        release_handler.create_release_bash_permission_files(
            release_template_file_names=config.RELEASE_TEMPLATE_FILES,
            release_templeate_path=config.BASE_TEMPLATE_PATH
        )
        
        # Set up default header templates for SQL files
        logger.info("Setting up SQL files' default header templates.")
        sql_files_default_headers_path = {
            'create': os.path.join(config.BASE_TEMPLATE_PATH, config.DEFAULT_HEADER_FILE_WITH_CREATE),
            'default': os.path.join(config.BASE_TEMPLATE_PATH, config.DEFAULT_HEADER_FILE)
        }

        # Create deployment guide in Word format
        logger.info("Creating deployment guide.")
        deploy_guide_word_file_path = os.path.join(config.BASE_TEMPLATE_PATH, config.RELEASE_DOCX)
        release_handler.create_deploy_guide_word_doc(
            deploy_guide_word_path=deploy_guide_word_file_path,
            word_doc_name=config.RELEASE_DOCX
        )
        
        # Create empty SQL release files
        logger.info("Creating empty SQL release files.")
        release_handler.create_empty_sql_release_files(
            sql_release_files=config.RELEASE_FILES,
            sql_files_default_headers_path=sql_files_default_headers_path
        )
        
        logger.info("Copying SQL files to the release directory.")
        release_handler.copy_sql_files_changed_to_release_file(release_file_mapping=config.RELEASE_FILE_MAPPING)

        logger.info("Release process completed successfully.")
    except ValueError as ve:
        logger.error("ValueError encountered: %s", ve, exc_info=True)
    except Exception as e:
        logger.error("Unexpected error occurred: %s", e, exc_info=True)
    
if __name__ == '__main__':
    # Validate command-line arguments
    if len(sys.argv) < 2:
        logging.error("No changes have been made to any sql files.")
        sys.exit(1)      
    
    # Extract release number and files changed from arguments    
    #python main.py <release_num> <files_changed 1,2,3..> <Prev tag> <Input Tag>
    files_changed_with_tags = sys.argv[2:]
    #extract release number as str
    release_number = sys.argv[1:2][0]
    
    logger.info("Starting the release process with release number: %s and files: %s", release_number, files_changed_with_tags)
    main(files_changed_with_tags=files_changed_with_tags, release_number=release_number)