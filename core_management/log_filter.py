
def log_for_case(url):
    split_url = url.split('/')
    message = ''
    try:
        if split_url[3]== "create":
            message = "case created"
            return message
        elif split_url[3]== "update":
            message = "case update"
            return message
        elif split_url[3]== "delete":
            message = "case delete"
            return message
        elif split_url[3]== "upload":
            message = "case upload"
            return message
        elif split_url[3]== "create_event":
            message = "create event"
            return message
        elif split_url[3]== "update_event":
            message = "update event"
            return message
        elif split_url[3]== "delete_event":
            message = "delete event"
            return message
        elif split_url[3]== "generate_commentors":
            message = "case Report Generation"
            return message
        elif split_url[3]== "view":
            message = "case view"
            return message
        elif split_url[3]== "case_detail":
            message = "case detail"
            return message
        elif split_url[3]== "add":
            try:
                if split_url[4]=="investigator":
                    message = "added investigator"
                    return message
                elif split_url[4]== "person":
                    message = "added person"
                    return message
                elif split_url[4]== "location":
                    message = "added location"
                    return message
                elif split_url[4]== "media":
                    message = "added media"
                    return message
                elif split_url[4]== "evidence":
                    message = "added evidence"
                    return message
                elif split_url[4]== "event":
                    message = "added event"
                    return message
                elif split_url[4]== "data":
                    message = "added data"
                    return message
            except:
                pass
        elif split_url[3] == "remove":
            try:
                if split_url[4]== "investigator":
                    message = "remove investigator"
                    return message
            except:
                pass
    except Exception as e:
        print('Log exception Case -->',e)

def log_for_portfolio(url, method):
    split_url = url.split('/')
    message = ''
    if split_url[3]=="all_portfolio":
        message = "All protfolio list"
        return message

    elif split_url[3] == 'individual':
        if method == "GET":
            message = ""
            return message
        elif method == "POST":
            message = "Porfolio create Individual"
            return message
        elif method == "PATCH" or method == "PUT":
            message = "Porfolio Update Individual"
            return message
        else: 
            message = "Porfolio delete Individual"
            return message

    elif split_url[3] == 'group':
        if method == "GET":
            message = ""
            return message
        elif method == "POST":
            message = "Porfolio create group"
            return message
        elif method == "PATCH" or method == "PUT":
            message = "Porfolio Update group"
            return message
        else: 
            message = "Porfolio delete group"
            return message
        
    elif split_url[3] == 'event':
        if method == "GET":
            message = ""
            return message
        elif method == "POST":
            message = "Porfolio create event"
            return message
        elif method == "PATCH" or method == "PUT":
            message = "Porfolio Update event"
            return message
        else: 
            message = "Porfolio delete event"
            return message

    elif split_url[3] == 'linked_data':
        if method == "GET":
            message = ""
            return message
        elif method == "POST":
            message = "Porfolio create linked data"
            return message
        elif method == "PATCH" or method == "PUT":
            message = "Porfolio Update linked data"
            return message
        else: 
            message = "Porfolio delete linked data"
            return message

    elif split_url[3] == 'keybase':
        if method == "GET":
            message = ""
            return message
        elif method == "POST":
            message = "Porfolio create keybase"
            return message
        elif method == "PATCH" or method == "PUT":
            message = "Porfolio Update keybase"
            return message
        else: 
            message = "Porfolio delete keybase"
            return message

    elif split_url[3] == 'user':
        if method == "GET":
            message = ""
            return message
        elif method == "POST":
            message = "Porfolio create user"
            return message
        elif method == "PATCH" or method == "PUT":
            message = "Porfolio Update user"
            return message
        else: 
            message = "Porfolio delete user"
            return message
     
    elif split_url[3]=="attach":
        if split_url[3]=="keybase":
            message = "Porfolio attach keybase"
            return message
        elif split_url[3]=="target":
            message = "Porfolio attach target"
            return message
        elif split_url[3]=="portfolio":
            message = "Porfolio attach portfolio"
            return message
        elif split_url[3]=="case":
            message = "Porfolio attach case"
            return message
        elif split_url[3]=="data":
            message = "Porfolio attach data"
            return message

def log_for_account_management(url, method):
    split_url = url.split('/')
    message = ''
    if split_url[3]=="create_profile":
        message = "Created Profile"
        return message
    elif split_url[3]=="update_profile":
        message = "update Profile"
        return message
    elif split_url[3]=="all_permissions":
        message = "list all permissions"
        return message
    elif split_url[3]=="login":
        message = "login"
        return message
    elif split_url[3]=="logout":
        message = "logout"
        return message
    elif split_url[3]=="team":
        message = "team"
        return message
    elif split_url[3]=="team_member":
        message = "team_member"
        return message
    elif split_url[3]=="add_user":
        if method == "GET":
            message = ""
            return message
        elif method == "POST":
            message = "Account add user"
            return message
        elif method == "PATCH" or method == "PUT":
            message = "Account Update user"
            return message
        else: 
            message = "Account delete user"
            return message

    elif split_url[3]=="add_group":
        if method == "GET":
            message = ""
            return message
        elif method == "POST":
            message = "Account add group"
            return message
        elif method == "PATCH" or method == "PUT":
            message = "Account Update group"
            return message
        else: 
            message = "Account delete group"
            return message

    elif split_url[3]=="add_profile":
        if method == "GET":
            message = ""
            return message
        elif method == "POST":
            message = "Account add profile"
            return message
        elif method == "PATCH" or method == "PUT":
            message = "Account Update profile"
            return message
        else: 
            message = "Account delete profile"
            return message

    elif split_url[3]=="accountsettings":
        if method == "GET":
            message = ""
            return message
        elif method == "POST":
            message = "Added Account settings"
            return message
        elif method == "PATCH" or method == "PUT":
            message = " Update Account settings"
            return message
        else: 
            message = "Delete Account settings"
            return message

def log_for_target_management(url, method):
    split_url = url.split('/')
    message = ''
    try:
        if split_url[3]=="social":
            if split_url[4]=="view":
                message = "social View"
                return message
            elif split_url[4]=="create":
                message = "social create"
                return message
            elif split_url[4]=="update":
                message = "social update"
                return message
            elif split_url[4]=="delete":
                message = "social delete"
                return message

        elif split_url[3]=="generic":
            if split_url[4]=="view":
                message = "Generic Target View"
                return message
            elif split_url[4]=="create":
                message = "Generic Target create"
                return message
            elif split_url[4]=="update":
                message = "Generic Target update"
                return message
            elif split_url[4]=="delete":
                message = "Generic Target delete"
                return message

        elif split_url[3]=="keybase":
            if split_url[4]=="view":
                message = "keybase Target View"
                return message
            elif split_url[4]=="create":
                message = "keybase Target create"
                return message
            elif split_url[4]=="update":
                message = "keybase Target update"
                return message
            elif split_url[4]=="delete":
                message = "keybase Target delete"
                return message

        elif split_url[3]=="get":
            if split_url[4]=="response":
                message = "Get Target response"
                return message
            elif split_url[4]=="linkanalysis":
                message = "link analysis perform"
                return message
            elif split_url[4]=="id_response":
                message = "Target id response"
                return message
            elif split_url[4]=="linkanalysis_explore":
                message = "link analysis explore"
                return message
            elif split_url[4]=="posts":
                message = "Target Post"
                return message
            elif split_url[4]=="followers":
                message = "Target followers"
                return message
            elif split_url[4]=="followings":
                message = "Target followings"
                return message

        elif split_url[3]=="delete":
            if split_url[4]=="elasticsearch":
                message = "Delete elasticsearch doc"
                return message
            elif split_url[4]=="hdfs":
                message = "Delete response hdfs"
                return message

        elif split_url[3]=="socialmedia":
            message = "view social media "
            return message
        
        elif split_url[3]=="add_socialmedia":
            message = "view add_socialmedia "
            return message

        elif split_url[3]=="update_socialmedia":
            message = "view update_socialmedia "
            return message

        elif split_url[3]=="delete_socialmedia":
            message = "view delete_socialmedia "
            return message

        elif split_url[3]=="periodic_targets" and split_url[4]=="update":
            message = "periodic targets updated"
            return message
        
        elif split_url[3]=="delete_socialmedia":
            message = "view delete socialmedia "
            return message
        
        elif split_url[3]=="smart":
            message = "smart target search"
            return message

        elif split_url[3]=="bulk":
            message = "bulk target View"
            return message

        elif split_url[3]=="survey":
            message = "Target search survey"
            return message
        
        elif split_url[3]=="updatestatus":
            message = "Target search update status"
            return message

    except Exception as  e:
        print("Exception in log target management --",e)
        pass

    message = "Created Profile"
    return message


def log_filter_url(url, method):
    split_url = url.split('/')
    message = ""
    try:
        if split_url[2]=='case':
            """ user for case urls only  """
            message = log_for_case(url)
        elif split_url[2]=='portfolio':
            message = log_for_portfolio(url, method)
        elif split_url[2]=='account':
            message = log_for_account_management(url, method)
        elif split_url[2]=='target':
            message = log_for_target_management(url, method)
        else:
            message = ""
    except:
        message = ""

    return message