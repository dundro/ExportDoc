import datetime
import json
from zeep import Client


def sysdate():
    return str(datetime.datetime.now())


def Init_Log():
    File_Name = Output_Folder + sysdate() + '.log'
    return open(File_Name, 'w')


def Log(Message, isSuccess, Id):
    Status = "SUCCESS" if isSuccess else "ERROR"
    print(sysdate(), Status, Message, Id, sep=';', file=Log_File)
    Log_File.flush()

def SaveAttachmentByApplicationId(Application_Id, Siebel_Attachment_Service):

    try:
        Siebel_Response = Siebel_Attachment_Service.getOptyData(
            IntegrationId=Application_Id, FileType='Page Passport 2')
        File_To_Save = Siebel_Response.Oppty.Doc[0].FileBuffer
        File_Extension = Siebel_Response.Oppty.Doc[0].FileExt
        outputfile = open(Output_Folder + Application_Id +
                          '.' + File_Extension, 'wb')
        outputfile.write(File_To_Save)
        outputfile.close()
        Log("file successfully saved", True, Application_Id)
    except AttributeError:
        Log("no attachment found", False, Application_Id)
    except BaseException as err:
        Log(err, False, Application_Id)


def GetApplicationsArray():
    try:
        Input_File = open(Input_File_Path, 'r')
    except FileNotFoundError:
        Log("File " + Input_File_Path + " not found", False, Application_Id)
        return []
    else:
        ApplicationsArray = []
        for Application_Id in Input_File:
            ApplicationsArray.append(Application_Id.strip(',\n'))
        Input_File.close()
        return ApplicationsArray


def main():

    client = Client(
        'wsdl/GetOpty.wsdl')
    Siebel_Attachment_Service = client.create_service('{http://siebel.com/CustomUI}ATC_spcGet_spcOpportunity_spcData_spcContactSys',
                                                      Siebel_WS_Endpoint)
    for Application_Id in GetApplicationsArray():
        SaveAttachmentByApplicationId(
            Application_Id, Siebel_Attachment_Service)


try:
    with open('options.json') as data_file:
        options = json.load(data_file)
except FileNotFoundError:
    print("Options file doesn't exist")
Siebel_WS_Endpoint = options["Service_Endpoint"]
Input_File_Path = options["Input_File_Path"]
Output_Folder = options["Output_Folder"]
Log_File = Init_Log()
Log('options loaded successfully;' + str(options), True, '')
main()
Log_File.close()
