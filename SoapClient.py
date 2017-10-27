import datetime
import json
import multiprocessing
from zeep import Client


def sysdate():
    return datetime.datetime.now().strftime('%d%m%Y_%H%M%S')


def Init_Log():
    File_Name = sysdate() + '.log'
    return open(File_Name, 'w')


def Log(Message, isSuccess, Id, Method, *args):
    Status = "SUCCESS" if isSuccess else "ERROR"
    print(multiprocessing.current_process, sysdate(),
          Status, Method, Message, Id, ';'.join(args), sep=';', file=Log_File)
    Log_File.flush()


def SaveAttachmentByApplicationId(Application_Id):

    try:
        Siebel_Response = Siebel_Attachment_Service.getOptyData(
            IntegrationId=Application_Id, FileType='Page Passport 2')
    except BaseException as err:
        print(err)
        Log(err, False, Application_Id, 'SaveAttachmentByApplicationId')
        outputfile = open('./Files/Log/' + Application_Id +
                          '_response.xml', 'w')
        outputfile.write(str(Siebel_Response))
    else:
        try:
            for idx, doc in enumerate(Siebel_Response.Oppty.Doc):
                Data_To_Be_Saved = doc.FileBuffer
                File_Extension = doc.FileExt
                Output_FileName = Application_Id + '_' + str(idx)+ '.' + File_Extension
                # print('found file'+doc.FileName)
                outputfile = open(Output_Folder + Output_FileName, 'wb')
                outputfile.write(Data_To_Be_Saved)
                Log("file successfully saved", True,
                    Application_Id, 'SaveAttachmentByApplicationId', Output_FileName)
        except AttributeError:
            Log("no attachment found", False, Application_Id,
                'SaveAttachmentByApplicationId')
            outputfile = open(
                './Files/Log/' + Application_Id + '_response.xml', 'w')
            outputfile.write(str(Siebel_Response))
        except BaseException as err:
            print('Error occured \n')
            print(err)
            Log(err, False, Application_Id, 'SaveAttachmentByApplicationId')
            outputfile = open('./Files/Log/' + Application_Id +
                              '_response.xml', 'w')
            outputfile.write(str(Siebel_Response))
    finally:
        outputfile.close()


def GetApplicationsArray(Input_Path):
    try:
        Input_File = open(Input_Path, 'r')
    except FileNotFoundError:
        Log("File " + Input_Path + " not found", False,
            Application_Id, 'GetApplicationsArray')
        return []
    else:
        ApplicationsArray = []
        for Application_Id in Input_File:
            ApplicationsArray.append(Application_Id.strip(',\n'))
        Input_File.close()
        return ApplicationsArray


def popAppfromList(Application_Id):
    SaveAttachmentByApplicationId(
        Application_Id)


def main(Input_Path):
    arr = GetApplicationsArray(Input_Path)
    # for app in arr:
    #     popAppfromList(app)
    with multiprocessing.Pool(5) as p:
        p.map(popAppfromList, arr)


if __name__ == '__main__':
    try:
        with open('options.json') as data_file:
            options = json.load(data_file)
    except FileNotFoundError:
        print("Options file doesn't exist")
    Siebel_WS_Endpoint = options["Service_Endpoint"]
    Input_File_Path = options["Input_File_Path"]
    Output_Folder = options["Output_Folder"]
    client = Client(
        'wsdl/GetOpty.wsdl')
    Siebel_Attachment_Service = client.create_service('{http://siebel.com/CustomUI}ATC_spcGet_spcOpportunity_spcData_spcContactSys',
                                                      Siebel_WS_Endpoint)
    Log_File = Init_Log()
    # Log('options loaded successfully;' + str(options), True, '')
    main(Input_File_Path)
    Log_File.close()
