if value != "":
    try:
        value = FileObject(url_to_path(value))
        if value.is_version and VERSIONS_BASEDIR:
            final_attrs['directory'] = os.path.split(value.original.path_relative)[0]
        else:
            final_attrs['directory'] = os.path.split(value.path_relative)[0]
    except:
        pass