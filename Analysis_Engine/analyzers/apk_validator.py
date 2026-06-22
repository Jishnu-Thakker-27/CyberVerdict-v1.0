import zipfile
def check_file_exist(apk):
    file_exist={}
    
    try:
        with open (f"{apk}") as f:
            file_exist["success"]=True
            return file_exist
    except Exception as e:
        file_exist["success"]=False
        file_exist["stage"]="file_existence_check"
        file_exist["reason"]="APK file not found"
        file_exist["techincal details"]=str(e)
        return file_exist

    
def check_extension(apk):
    extension_exist={}
    if f"{apk}".endswith(".apk"):
        extension_exist["success"]=True
        extension_exist["apk_extension"]=True
        return extension_exist
    else:
        extension_exist["success"]=False
        extension_exist["apk_extension"]=False
        extension_exist["stage"]="file_extension_check"
        extension_exist["reason"]="File is not a apk application"
        extension_exist["technical details"]=".apk extension not found"
        return extension_exist
        
        
def check_zip(apk):
    zip_exist={}
    if  zipfile.is_zipfile(apk):
        zip_exist["success"]=True
        zip_exist["zip_file"]=True
        return zip_exist
    else:
        zip_exist["success"]=False
        zip_exist["zip_file"]=False
        zip_exist["stage"]="zip_file_check"
        zip_exist["reason"]="File is not a apk application"
        zip_exist["technical details"]="File do not contain zip archive"
        return zip_exist
        

def check_manifest(apk):
    zip_exist_for_manifest=check_zip(apk)
    if zip_exist_for_manifest["success"]: 
        manifest_exist={}
        if f"{apk}".endswith("AndroidManifest.xml"):
            manifest_exist["success"]=True
            manifest_exist["apk_extension"]=True
            return manifest_exist
        else:
            manifest_exist["success"]=False
            manifest_exist["apk_extension"]=False
            manifest_exist["stage"]="manifest_file_extension_check"
            manifest_exist["reason"]="File is not a apk application"
            manifest_exist["technical details"]="Android.xml not found"
            return manifest_exist
    else:
        return zip_exist_for_manifest

def check_dex(apk):
    pass
            
    
            
        
        