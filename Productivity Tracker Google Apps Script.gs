const ss = SpreadsheetApp.getActiveSpreadsheet();
const sheet = ss.getSheetByName('Employee Productivity Tracking');
const logSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("LogSheet");
const employeeDatabaseSheetName = 'Employees Database';

function doPost(e) 
{

  try 
  {
    var postData = JSON.parse(e.postData.contents);
    
    if (!sheet) 
    {
      throw new Error('Sheet named ' + sheetName + ' not found.');
    }

    // Parse the incoming JSON data
    var data = postData;

    // Row number for the formulas (to use in the formula strings)
    var rowNumber = sheet.getLastRow() + 1;

    // Construct the row array manually to ensure correct data conversion
    var row = 
    [
      data.email,
      data.mouse_clicks,
      data.key_presses,
      data.current_project,
      data.open_programs.join(', '),
      data.active_window_title,
      data.date,
      data.time_started,
      data.time_stopped,
      data.minutes_tracked,
      `=J${rowNumber}/60`,
      `=IFERROR(VLOOKUP(A${rowNumber},'${employeeDatabaseSheetName}'!A:C,2,FALSE)&" "&VLOOKUP(A${rowNumber},'${employeeDatabaseSheetName}'!A:C,3,FALSE), "Not Found")`,
    ];
    
    // Append the data to the next available row in the sheet
    sheet.appendRow(row);
    
    // Log successful decryption
    logSheet.appendRow([new Date(), "Success", JSON.stringify(decryptedData)]);
    return ContentService.createTextOutput(JSON.stringify({status: "success", data: decryptedData})).setMimeType(ContentService.MimeType.JSON);

  } 
  catch (error) 
  {
    // Log the error
    logSheet.appendRow([new Date(), "Error", error.message]);
    
    return ContentService.createTextOutput(JSON.stringify({status: "error", message: error.message})).setMimeType(ContentService.MimeType.JSON);
  }
}
