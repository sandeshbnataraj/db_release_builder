import os
import sys
import docx
import logging

logger = logging.getLogger(__name__)

class ReleaseResourceManager():
    def __init__(self, awb_agt_release_file_path, file_manager_ref, bgt_release_handler_ref):
        self.awb_agt_release_file_path = awb_agt_release_file_path
        self.release_dirs_with_db_paths = None
        self.file_manager_ref = file_manager_ref
        self.bgt_release_handler_ref = bgt_release_handler_ref
    
    def create_empty_directories(self, database_names):
        """
        Create directories for the given paths if they don't already exist.
        """
        created_directories = []
        for database_name in  database_names:
            try:
                # Build the full path and create the directories
                release_full_path_with_db_name = os.path.join(self.awb_agt_release_file_path, database_name)
                os.makedirs(release_full_path_with_db_name, exist_ok=True)
                    
                # Add the created directory to the list
                created_directories.append(release_full_path_with_db_name)
                    
                # Log the directory creation
                logger.info(f"Directory created or already exists: {release_full_path_with_db_name}")
            
            except Exception as e:
                logger.error(f"Failed to create directory {release_full_path_with_db_name}: {e}")
                sys.exit(1)
            # Try else will excute only when try block is successful
            #else:
                #create_deploy_word(f"AWB_{awb_new_version}_AND_AGT_{agt_new_version}",file_version_number)

        if created_directories:
            self.release_dirs_with_db_paths = created_directories    
            # Return the list of created directories
            return created_directories
    
    def generate_release_bash_and_permission_files(self, file_path, file_name):
        """
        Create release bash files for each path in paths with appropriate modified data.
        """
        bash_file_data = self.file_manager_ref.read_file_content(file_path=file_path)
        for release_dir_db_path in self.release_dirs_with_db_paths:
            replaced_file_content = self.bgt_release_handler_ref.file_replacements(file_content=bash_file_data, release_db_file_path=release_dir_db_path, sql_release_file_name=None)  
            bash_release_file_path = os.path.join(release_dir_db_path, file_name)
            self.file_manager_ref.write_file_content(file_path=bash_release_file_path, file_content=replaced_file_content)
            
    
    def generate_empty_release_sql_files(self, sql_release_files, sql_files_default_headers_path):
        """
        Create release files for each path in paths with appropriate header data.
        """      
        default_sql_header_data = {
            'with_create_data': self.file_manager_ref.read_file_content(sql_files_default_headers_path['create']),
            'defalt_data': self.file_manager_ref.read_file_content(sql_files_default_headers_path['default'])
        }
        
        for release_dir_db_path in self.release_dirs_with_db_paths:
            for sql_release_file_name in sql_release_files:
                # Determine the appropriate header data
                header_key = 'with_create_data' if sql_release_file_name == '1_datatrak_create_new_table_scripts.sql' else 'defalt_data'
                header_content = default_sql_header_data[header_key]
 
                replaced_file_content = (
                    self.bgt_release_handler_ref.file_replacements(
                        file_content=header_content,
                        release_db_file_path=release_dir_db_path ,
                        sql_release_file_name=sql_release_file_name
                    )                                   
                )
                
                # Construct the full file path
                sql_release_file_path = os.path.join(release_dir_db_path, sql_release_file_name)
                # Write the modified header data to the file
                self.file_manager_ref.write_file_content(file_path=sql_release_file_path, file_content=replaced_file_content)
                
    def get_release_sql_filename(sql, sql_file_changed_path, release_file_mapping):
        """
        Map the input file path to the correct release file name based on the directory.
        """
        logger.info(f"sql_file_path:{sql_file_changed_path}")
        # Ex: ./datatrak_bgt_agt/stored_procedures/<sp_name.sql>
        parts = sql_file_changed_path.split(os.sep)    
        if len(parts)<2:
            logger.warning(f"Invalide file path structure: {sql_file_changed_path}")
            return None
        sql_directory_name = parts[1]  # Get the directory name (e.g., 'stored_procedures')
        release_db_name = parts[0]  # Get the DB name (e.g., 'datatrak_bgt_agt')

        # Return the corresponding release file name or None if not found
        return release_file_mapping.get(sql_directory_name, None), release_db_name
    
    
    def copy_sql_files_to_release_files(self, sql_file_changed_paths, release_file_mapping):
        """
        Copy the contents of a file to the appropriate release file based on its directory.
        """
        logger.info(f"sql_file_changed_paths:{sql_file_changed_paths}")
        for sql_file_path in sql_file_changed_paths:
            logger.info(f"sql_file_path:{sql_file_path}")
            release_sql_file_name, release_db_name = self.get_release_sql_filename(sql_file_changed_path=sql_file_path, release_file_mapping=release_file_mapping)
            if release_sql_file_name:
                for release_dir_db_path in self.release_dirs_with_db_paths:
                    if release_db_name in release_dir_db_path:
                        sql_release_full_path = os.path.join(release_dir_db_path,release_sql_file_name)
                        self.file_manager_ref.copy_file(target_file_path=sql_file_path, final_release_path=sql_release_full_path)
            else:
                logger.warning(f"No matching release file for {sql_file_changed_paths}")
                
    def generate_deploy_guide_word_doc(self, release_number, deploy_guide_word_path, word_doc_name):
        # Dictionary to map placeholders to replacement values
        replace_dict = {
            'file_name': self.awb_agt_release_file_path,
            'version': release_number
        }
        
        self.file_manager_ref.write_to_deploy_guide_word(deploy_guide_word_path=deploy_guide_word_path, replace_dict=replace_dict,
                                                         word_doc_name=word_doc_name)