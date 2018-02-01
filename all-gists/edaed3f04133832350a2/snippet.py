from shutil import make_archive, move, rmtree
import os

class Archiver:
    
    def __init__(self):
        self.local_dir = '/home'
        self.archive_dir = '/home/archive'
        self.archive_name = os.path.join(self.local_dir, 'zip_archive')
        
    
    
    def file_search(self):
        """
            Search for ZIP files
        """
        file_list = []
        
        for i in os.listdir(self.local_dir):
            if os.path.splitext(i)[1] == '.zip':
                file_list.append(i)
        
        return file_list
    
    
    
    def move_files(self):
        """
            Move ZIP files to archive directory. It will be a base directory for archiving
        """
        if len(self.file_search()) > 0:
            if os.path.exists(self.archive_dir):
                rmtree(self.archive_dir)
                if not os.path.exists(self.archive_dir):
                    os.makedirs(self.archive_dir)
                    if os.path.exists(self.archive_dir):
                        for i in self.file_search():
                            move(os.path.join(self.local_dir,i),self.archive_dir)
            
                        print("Successfully Moved")
                        return True
                    else:
                        print("Move Failed")
                        return False
            else:
                if not os.path.exists(self.archive_dir):
                    os.makedirs(self.archive_dir)
                    if os.path.exists(self.archive_dir):
                        for i in self.file_search():
                            move(os.path.join(self.local_dir,i),self.archive_dir)
            
                        print("Successfully Moved")
                        return True
                    else:
                        print("Move Failed")
                        return False
                
        else:
            print("Move Failed, There no such files to move")
            return False
            
    
    
    def create_tar_gz(self):
        """
            Creating Archive File.
        """
        if self.move_files():        
            
            try:
                make_archive(self.archive_name, 'gztar', self.archive_dir)
            except Exception as exc:
                print(type(exc), exc)
            else:
                print("success! Archive file created!")
                return True
        else:
            print("Nothing Happened!!")
            return False
        
    
    def cleaning_operation(self):
        if self.create_tar_gz():
            rmtree(self.archive_dir)
        
  
x = Archiver()
x.cleaning_operation()