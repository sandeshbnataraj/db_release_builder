import logging
import sys
import os
import chardet
import docx
from datetime import datetime

logger = logging.getLogger(__name__)

class FilesManager():
    def __init__(self):
        """
        Initialize the FilesManager class.
        """
        pass
    
    def detect_encoding(self, file_path:str) -> str:
        """
        Detect the encoding of a file.
        """
        try:
            with open(file_path, 'rb') as rf:
                data = rf.read(4096) # Read only first 4 KB 
        
            # Use chardet to detect the encoding
            result = chardet.detect(data)
            logger.info(f"Detected encoding for {file_path}: {result}")
            return result['encoding']
        
        except UnicodeDecodeError:
            logger.error(f"Unable to decode file {file_path}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            sys.exit(1)
       
    def read_file_content(self, file_path:str) -> str:
        """
        Read the content of a file using its detected encoding.
        """
        try:
            # Detect file encoding
            current_encoding = self.detect_encoding(file_path)
            if not current_encoding:
                raise ValueError("Failed to detect file encoding.")
            
            # Open and read the file using the detected encoding
            with open(file_path, 'r', encoding=current_encoding.lower()) as rf:
                data = rf.read() 
            
            logger.info(f"File {file_path} read successfully.")
            return data
        
        except FileNotFoundError:
            logger.error(f"File {file_path} not found.")
            sys.exit(1)
        except ValueError as ve:
            logger.error(f"Encoding detection error: {ve}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            sys.exit(1)
          
    def write_file_content(self, file_path:str, file_content:str) -> None:
        """
        Write content to a file, creating or overwriting it.
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as wf:
                wf.write(file_content)
            
            logger.info(f"Written to file: {file_path}")
        
        except Exception as e:
            logger.error(f"Failed to write to file {file_path}: {e}")
    
    def apply_file_replacements(self, file_content, db_versions_dict, release_dir_with_db_name, sql_release_file_name):
        """
        Apply placeholder replacements to the data.
        """
        if sql_release_file_name:
            file_content = self.apply_sql_file_replacments(
                    file_content=file_content, 
                    sql_release_file_name=sql_release_file_name
                )
        
        # os.path.basename extracts everything after the last / in the path: release/AWB_<version>_and_AGT_<version>/<db_name>
        release_db_file_name = os.path.basename(release_dir_with_db_name)
        file_content = self.replace_text_in_file(
                file_content=file_content, 
                target_text='deployment_db_name', 
                replacement_text=release_db_file_name
            )
        
        db_version_tuple = self.get_versions_tuple(
            db_versions_dict=db_versions_dict, release_db_file_name=release_db_file_name
        )
        
        if not db_version_tuple:
            logger.error("No DB versions in dict")
            sys.exit(1)
            
        old_version, new_version = db_version_tuple

        file_content = self.replace_text_in_file(
                file_content=file_content, 
                target_text='old_version', 
                replacement_text=f"'{old_version}'"
            )
        file_content = self.replace_text_in_file(
                file_content=file_content, 
                target_text='new_version', 
                replacement_text=f"'{new_version}'"
            )
        
        return file_content
            
    def replace_text_in_file(self, file_content, target_text, replacement_text):
        """
        Replace text in the file content.
        """
        return file_content.replace(target_text, replacement_text)
        
    def apply_sql_file_replacments(self, file_content, sql_release_file_name):
        """
        Replace placeholders specific to SQL files.
        """
        file_content = self.replace_text_in_file(
                file_content=file_content, 
                target_text='title_based_on_script', 
                replacement_text=sql_release_file_name
            )
        file_content = self.replace_text_in_file(
                file_content=file_content, 
                target_text='strdatetime', 
                replacement_text=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

        return file_content
    
    def get_versions_tuple(self, db_versions_dict, release_db_file_name):
        """
        Get old and new version tuples based on DB file name.
        """
        db_version_tuple = None
        # Select the correct version replacement tuple
        if 'agt' in release_db_file_name:
            db_version_tuple = db_versions_dict['agt']
        elif 'awb' in release_db_file_name:
            db_version_tuple = db_versions_dict['awb']
        else:
            logger.error(f"Unknown path basename: {release_db_file_name}")
            return None
        
        return db_version_tuple
    
    def copy_file(self, target_file_path, final_release_path):
        """
        Copies content from a source file to a destination file, converting to UTF-8 encoding.
        """
        try:
            curr_encoding = self.detect_encoding(file_path=target_file_path)
            with open(target_file_path,'r',encoding=curr_encoding.lower()) as rf, \
                open(final_release_path,'a',encoding='utf-8') as wf:
                    for line in rf:
                        wf.write(line)  
                    wf.write('\n\n')
                    logger.info(f"Copied {target_file_path} to {final_release_path}")

            logger.info(f"Copied {target_file_path} to {final_release_path}")
                 
        except UnicodeError:
            logger.error(f"Encoding error with file {target_file_path}. Ensure it is UTF-16 encoded.")
        except FileNotFoundError:
            logger.error(f"Source file {target_file_path} not found.")
        except Exception as e:
            logger.error(f"Error copying {target_file_path} to {final_release_path}: {e}")
           
            
    def write_to_deploy_guide_word(self, deploy_guide_word_path, replace_dict, word_doc_name):
        """
        Modify and save a Word document based on placeholders.
        """
        try:
            # Load the Word document template
            doc = docx.Document(deploy_guide_word_path)
            
            # Loop through each paragraph in the document
            for para in doc.paragraphs:
                # Loop through each run in the paragraph
                for run in para.runs:
                    # Check for each placeholder in the dictionary
                    for placeholder, new_text in replace_dict.items():
                        # If the run contains the placeholder text
                        if placeholder in run.text:
                            # Replace the text within the run, preserving the formatting
                            run.text = run.text.replace(placeholder, new_text)
            
            # Save the modified document to the new file path
            doc.save(word_doc_name)
            logger.info(f"Created the word document: {word_doc_name}")
        
        except Exception as e:
            logger.error(f"Failed to create word document: {e}")
    
   