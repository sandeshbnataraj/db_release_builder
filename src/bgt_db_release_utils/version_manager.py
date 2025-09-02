import os
import sys
import re
import logging

logger = logging.getLogger(__name__)

class VersionManager():
    def __init__(self, files_changed_with_tags, agt_file_data, awb_file_data):
        self.files_changed_with_tags = files_changed_with_tags
        self.agt_file_data = agt_file_data
        self.awb_file_data = awb_file_data
    
    def fetch_db_versions(self) -> dict:
        db_versions = {}
        
        if self.agt_file_data and self.awb_file_data:
            db_versions = self.fetch_versions_from_file()
            logger.info(f"inside fetch_db_versions{db_versions}")
        else:
            db_versions = self.fetch_versions_from_input()
        
        return db_versions
    
    def fetch_versions_from_input(self) -> dict:
        db_versions = {}

        # Extrace previous and current versions from input string
        previous_version, current_version = self.files_changed_with_tags[-2:]
        try:
            # Extract AGT and AWB old and new versions
            split_previous_version = previous_version.split('_and_')
            agt_old_version = split_previous_version[0].split('AGT_',1)[1]
            awb_old_version = split_previous_version[1].split('AWB_', 1)[1]
                
            split_current_version = current_version.split('_and_')
            agt_new_version = split_current_version[0].split('AGT_', 1)[1].replace('-b', '-B')
            awb_new_version = split_current_version[1].split('AWB_', 1)[1].replace('-b', '-B')     
                
            db_versions['agt'] = (agt_old_version, agt_new_version)
            db_versions['awb'] = (awb_old_version, awb_new_version)       

            return db_versions
        
        except Exception as e:
            logger.error(f"Error parsing versions from input: {e}")
            sys.exit(1)
    
    def parse_db_version_from_file(self, file_data:str) -> tuple:
        new_version_pattern = r"new_version=(.+)"
        old_version_pattern = r"old_version=(.+)"
    
        try:
            # Search for new and old versions using regular expressions
            new_version_match = re.search(new_version_pattern,file_data)
            old_version_match = re.search(old_version_pattern,file_data)
            
            # Extract new and old version if available
            if new_version_match:
                new_version = new_version_match.group(1).strip().replace('-b', '-B')      
            if old_version_match:
                old_version = old_version_match.group(1).strip().replace('-b', '-B')
            logger.info(f"inside parse_db_version_from_file{old_version}{new_version}")
            
            return (old_version,new_version)
        
        except Exception as e:
            logger.error(f"Error reading version information: {e}")
            
    def fetch_versions_from_file(self) -> dict:
        try:
            db_versions = {}
            db_versions['agt'] = self.parse_db_version_from_file(file_data=self.agt_file_data)
            db_versions['awb'] = self.parse_db_version_from_file(file_data=self.awb_file_data)
            logger.info(f"inside fetch_versions_from_file{db_versions}")
            return db_versions            
        
        except Exception as e:
            logger.error(f"Error parsing versions: {e}")