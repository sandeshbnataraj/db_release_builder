import os
import sys
import logging
from bgt_db_release_utils import (
        VersionManager,
        FilesManager,
        ReleaseResourceManager
    )

logger = logging.getLogger(__name__)

class BGTReleaseHandler():
    """
    A handler class for managing BGT database release processes.
    """
    def __init__(self, files_changed_with_tags, release_number):
        """
        Initialize the release handler with file changes and release details.
        """
        self.files_changed_with_tags = files_changed_with_tags
        self.release_number = release_number
        
        # Initialize attributes to hold file paths and versions
        self.sql_file_changed_paths = None
        self.db_versions_dict = None
        self.awb_agt_release_file_path = None
        self.release_dirs_with_db_name = None
        
        # Initialize utility managers
        self.file_manager = FilesManager()
        self.version_manager = None 
        self.release_manager = None
    
    def check_version_in_input(self) -> bool:
        """
        Check if version information exists in the input. If not, prepare to process file paths.
        """
        if len(self.files_changed_with_tags) > 2 and not os.path.isfile(self.files_changed_with_tags[-2])\
            and not os.path.isfile(self.files_changed_with_tags[-1]):
                 # Exclude last two inputs as they are assumed to be version strings
                self.sql_file_changed_paths = self.files_changed_with_tags[:-2] 
                return True
        else:
                # All inputs are treated as file paths
                self.sql_file_changed_paths = self.files_changed_with_tags
                return False
            
    def get_versions_file_data(self, version_file_paths:dict) -> tuple:
        """
        Retrieve content from version files.
        """
        agt_file_data = self.file_manager.read_file_content(file_path=version_file_paths['agt'])
        awb_file_data = self.file_manager.read_file_content(file_path=version_file_paths['awb']) 
        
        if agt_file_data and awb_file_data:
            return agt_file_data, awb_file_data
        else:
            sys.exit(1)
    
    def initialize_version_manager(self, agt_file_data:str, awb_file_data:str) -> None:
        """
        Initialize the VersionManager with AGT and AWB data.
        """
        self.version_manager = VersionManager(
                files_changed_with_tags=self.files_changed_with_tags,
                agt_file_data=agt_file_data,
                awb_file_data=awb_file_data
            )
    
    def get_db_versions(self) -> dict: 
        """
        Fetch database versions from the VersionManager.
        """
        db_versions_dict = self.version_manager.fetch_db_versions()
        logger.info(f"Database versions retrieved: {db_versions_dict}")
        if db_versions_dict:
            return db_versions_dict
        else:
            logger.error("No database versions found.")
            sys.exit(1)

    def set_db_versions_dict(self, db_versions_dict) -> None:
        """
        Set the database versions in the handler.
        """
        self.db_versions_dict = db_versions_dict
    
    def generate_awb_agt_release_file_path(self, release_dir_name:str) -> str:
        """
        Generate a path for the AWB and AGT release file.
        """
        agt_new_version = self.db_versions_dict['agt'][1]
        awb_new_version = self.db_versions_dict['awb'][1]           
        
        # Generate the file path
        awb_agt_release_file_name =  f"AWB_{awb_new_version}_AGT_{agt_new_version}"
        awb_agt_release_file_path = os.path.join(release_dir_name, awb_agt_release_file_name)
        
        return awb_agt_release_file_path
    
    def initialize_release_path_and_resource_manager(self, awb_agt_release_file_path:str) -> None:
        """
        Initialize the ReleaseResourceManager with the release file path.
        """
        self.awb_agt_release_file_path = awb_agt_release_file_path
        if self.awb_agt_release_file_path:
            self.release_resource_manager = ReleaseResourceManager(
                    awb_agt_release_file_path=self.awb_agt_release_file_path,
                    file_manager_ref=self.file_manager,
                    bgt_release_handler_ref=self
                )
        else:
            logger.error("Failed to initialize the release path.")
            sys.exit(1)
        
    def create_empty_release_directories(self, release_db_dir_names:str) -> str:
        """
        Create empty directories for release.
        """
        release_directories = self.release_resource_manager.create_empty_directories(
            database_names=release_db_dir_names
        )
        if release_directories:
            return release_directories
        else:
            logger.error("Failed to create release directories.")
            sys.exit(1)
    
    def set_release_dirs_with_db_name(self, release_dirs_with_db_name:str) -> str:
        """
        Set release directories with database names.
        """
        self.release_dirs_with_db_name = release_dirs_with_db_name
        
    def file_replacements(self, file_content:str, release_db_file_path:str, sql_release_file_name:str) -> str:
        """
        Apply replacements to file content.
        """
        return self.file_manager.apply_file_replacements(
                file_content=file_content, 
                db_versions_dict=self.db_versions_dict,
                release_dir_with_db_name=release_db_file_path,
                sql_release_file_name=sql_release_file_name
            )

    
    def create_deploy_guide_word_doc(self,deploy_guide_word_path, word_doc_name):
        """
        Create a Word document for deployment guide.
        """
        self.release_resource_manager.generate_deploy_guide_word_doc(release_number=self.release_number,
                                                                     deploy_guide_word_path=deploy_guide_word_path,
                                                                     word_doc_name=word_doc_name)
    
    def create_release_bash_permission_files(self, release_template_file_names, release_templeate_path):
        """
        Create bash and permission files for the release.
        """
        for release_template_file_name in release_template_file_names:
            release_template_file_path = os.path.join(release_templeate_path,release_template_file_name) 
            self.release_resource_manager.generate_release_bash_and_permission_files(
                    file_path=release_template_file_path,
                    file_name=release_template_file_name
                )
            
    def create_empty_sql_release_files(self, sql_release_files, sql_files_default_headers_path):
        """
        Create empty SQL release files with headers.
        """
        self.release_resource_manager.generate_empty_release_sql_files(
            sql_release_files=sql_release_files,
            sql_files_default_headers_path=sql_files_default_headers_path
        )
        
    def copy_sql_files_changed_to_release_file(self, release_file_mapping):
        """
        Copy changed SQL files to the release directory.
        """
        
        self.release_resource_manager.copy_sql_files_to_release_files(
            sql_file_changed_paths=self.sql_file_changed_paths, 
            release_file_mapping=release_file_mapping
        )
    