# Airtable Base Schema

## Table: Workers

**ID:** `tblC0qoL9psk68IqJ`

### Fields

| Name | ID | Type | Description | Options |
|------|----|----|-------------|--------|
| WorkerID | `fldqeW93mz0JZPrhX` | autoNumber |  |  |
| Name | `fldBi6qCZRCGteGc4` | singleLineText |  |  |
| Email | `fldjNug3kmAP4kTMg` | singleLineText |  |  |
| PhoneNumber | `fldKtKnjfnooAZgMh` | singleLineText |  |  |
| Photo | `fldkOBActPCBjkwwl` | multipleAttachments |  | {"isReversed":true} |
| Location | `fldZkgab9LzncOZWZ` | singleSelect |  | {"choices":[{"id":"selt7A7u38r9gUJ1D","name":"Tesla","color":"blueLight2"},{"id":"selFSG8jwbGWeQAHn","name":"Lubinsky 1","color":"cyanLight2"},{"id":"sel99IKLWhUc63C11","name":"Lubinsky 2","color":"tealLight2"},{"id":"seltCnZVa2XqtK3NI","name":"Zeeker","color":"greenLight2"}]} |
| Username | `fldCiiueXOO0DHlR3` | singleLineText |  |  |
| Password | `fldCbx6HJdXu4GyOH` | singleLineText |  |  |
| Role | `fldIEONuTX5LRCPB2` | singleLineText |  |  |
| LastLogin | `fldxfwikKDUU6OmuP` | dateTime |  | {"dateFormat":{"name":"iso","format":"YYYY-MM-DD"},"timeFormat":{"name":"12hour","format":"h:mma"},"timeZone":"client"} |
| TotalScans | `fldsSKfM3mEsm080k` | rollup |  | {"isValid":true,"recordLinkFieldId":"fldBFfqBXJW1CnpuY","fieldIdInLinkedTable":"fld1RlzvBPoTgklIy","referencedFieldIds":[],"result":{"type":"number","options":{"precision":0}}} |
| LastScan | `fldAFD1t3tjrwQoC0` | date |  | {"dateFormat":{"name":"local","format":"l"}} |
| Scans (Worker) | `fldBFfqBXJW1CnpuY` | multipleRecordLinks |  | {"linkedTableId":"tbl9UAOJQRWv9k1Y0","isReversed":false,"prefersSingleRecordLink":false,"inverseLinkFieldId":"fldfSmWzNbbfYwu3u"} |
| Scans (Location) | `fldovWXsyMTBnzCSn` | singleLineText |  |  |
| Vehicles (LastLocation) | `fldRWeSXkjEzlabjE` | singleLineText |  |  |
| Vehicles (LastWorker) | `fldFjWzHclelYutNO` | multipleRecordLinks |  | {"linkedTableId":"tbl7rl82Y64bEuxTQ","isReversed":false,"prefersSingleRecordLink":false,"inverseLinkFieldId":"fld9heJWfKoCPZicp"} |
| DailyReports | `fldD7mTGFCHSAVjYu` | singleLineText |  |  |
| DailyReports 2 | `fld9M9ubpMWhjKNcn` | singleLineText |  |  |
| Table 7 | `fld3wpNIiUOy262ZC` | multipleRecordLinks |  | {"linkedTableId":"tblEPkLKKt2D4UIqU","isReversed":false,"prefersSingleRecordLink":false,"inverseLinkFieldId":"fldr2p5nE8qh8Arch"} |
| Polish | `flddQOmpveaPje8WM` | multipleRecordLinks |  | {"linkedTableId":"tblpNTCIBes9RkLmi","isReversed":false,"prefersSingleRecordLink":false,"inverseLinkFieldId":"fldl09Do7NCt4sjmQ"} |

## Table: Vehicles

**ID:** `tbl7rl82Y64bEuxTQ`

### Fields

| Name | ID | Type | Description | Options |
|------|----|----|-------------|--------|
| VehicleID | `fldqlW7Q0gz87xaCZ` | autoNumber |  |  |
| LicensePlate | `fldU3bHOICNVolEOP` | singleLineText |  |  |
| Polish photo | `fldDkC5PuW2uC9PFv` | multipleLookupValues |  | {"isValid":true,"recordLinkFieldId":"fldRLFfChzrhvyPuc","fieldIdInLinkedTable":"fldDAauquEXLjzZUu","result":{"type":"multipleAttachments","options":{"isReversed":false}}} |
| Color | `fldqhvl1SiYp9Yh0y` | singleLineText |  |  |
| Photo | `fldUsYjkDNAZZP7Co` | multipleLookupValues |  | {"isValid":true,"recordLinkFieldId":"fldBZpM5iLEsWe04b","fieldIdInLinkedTable":"fldpScbzmXa8c2h2r","result":{"type":"multipleAttachments","options":{"isReversed":true}}} |
| TotalScans | `fldCOskkL0fnfv1y1` | rollup |  | {"isValid":true,"recordLinkFieldId":"fldBZpM5iLEsWe04b","fieldIdInLinkedTable":"fld1RlzvBPoTgklIy","referencedFieldIds":[],"result":{"type":"number","options":{"precision":0}}} |
| FirstSeen | `fld5cgLluKre1H4E3` | dateTime |  | {"dateFormat":{"name":"iso","format":"YYYY-MM-DD"},"timeFormat":{"name":"12hour","format":"h:mma"},"timeZone":"client"} |
| LastSeen | `fldjsorz4ODOHoQoJ` | dateTime |  | {"dateFormat":{"name":"iso","format":"YYYY-MM-DD"},"timeFormat":{"name":"12hour","format":"h:mma"},"timeZone":"client"} |
| LastWorker | `fld9heJWfKoCPZicp` | multipleRecordLinks |  | {"linkedTableId":"tblC0qoL9psk68IqJ","isReversed":false,"prefersSingleRecordLink":true,"inverseLinkFieldId":"fldFjWzHclelYutNO"} |
| DailyScanFlag | `fldvgtBr3HG0KlTBG` | checkbox |  | {"icon":"thumbsUp","color":"greenBright"} |
| Scans | `fldBZpM5iLEsWe04b` | multipleRecordLinks |  | {"linkedTableId":"tbl9UAOJQRWv9k1Y0","isReversed":false,"prefersSingleRecordLink":false,"inverseLinkFieldId":"fld77NVrjBEIVtYyW"} |
| CarDryers | `fld7i4gvdNfVo6HMa` | singleLineText |  |  |
| workId (from CarDryers) | `fldv8nTLulJm9yz53` | multipleLookupValues |  | {"isValid":false,"recordLinkFieldId":null,"fieldIdInLinkedTable":"fldda8BrILuaoTyBf","result":null} |
| Polish | `fldRLFfChzrhvyPuc` | multipleRecordLinks |  | {"linkedTableId":"tblpNTCIBes9RkLmi","isReversed":false,"prefersSingleRecordLink":false,"inverseLinkFieldId":"fldMae7AhVpYL2jfR"} |
| Services (from Polish) | `fldERKNSpZ4diJYG2` | multipleLookupValues |  | {"isValid":true,"recordLinkFieldId":"fldRLFfChzrhvyPuc","fieldIdInLinkedTable":"fldZuQttR2GzlaEkN","result":{"type":"singleSelect","options":{"choices":[{"id":"selu2qsO32P9rgVxR","name":"HalfPolish","color":"blueLight2"},{"id":"sellx7ITDv9O08gm7","name":"FullPolish","color":"cyanLight2"},{"id":"sellYkBqdHrcxHxMa","name":"Wash","color":"tealLight2"},{"id":"selRYlRPO6wlZtbLD","name":"Shlaif","color":"greenLight2"}]}}} |
| InvalidCharacters | `fld2VAFA106e7Z8rK` | formula |  | {"isValid":true,"formula":"REGEX_MATCH({fldU3bHOICNVolEOP}, \"[^0-9-]\")","referencedFieldIds":["fldU3bHOICNVolEOP"],"result":{"type":"number","options":{"precision":0}}} |
| InvalidLicensePlate | `fldvCATN19QljuYmq` | formula | Checks if LicensePlate contains either 0 or exactly 2 hyphens. | {"isValid":true,"formula":"IF(OR(LEN({fldU3bHOICNVolEOP}) = LEN(SUBSTITUTE({fldU3bHOICNVolEOP}, '-', '')), LEN({fldU3bHOICNVolEOP}) - LEN(SUBSTITUTE({fldU3bHOICNVolEOP}, '-', '')) = 2, FIND(':', {fldU3bHOICNVolEOP}), FIND('.', {fldU3bHOICNVolEOP}), FIND(' ', {fldU3bHOICNVolEOP})), 1, 0)","referencedFieldIds":["fldU3bHOICNVolEOP"],"result":{"type":"number","options":{"precision":0}}} |
| Make | `fldhyrMNSyBlZH90b` | singleLineText |  |  |
| Model | `fldtgGMPRNFuFW61f` | singleLineText |  |  |
| Year | `fldO5Y74BCDzRGWZl` | number |  | {"precision":0} |
| LastLocation | `fldRZm1Pk2qNg7f5S` | multipleLookupValues |  | {"isValid":true,"recordLinkFieldId":"fld9heJWfKoCPZicp","fieldIdInLinkedTable":"fldZkgab9LzncOZWZ","result":{"type":"singleSelect","options":{"choices":[{"id":"selt7A7u38r9gUJ1D","name":"Tesla","color":"blueLight2"},{"id":"selFSG8jwbGWeQAHn","name":"Lubinsky 1","color":"cyanLight2"},{"id":"sel99IKLWhUc63C11","name":"Lubinsky 2","color":"tealLight2"},{"id":"seltCnZVa2XqtK3NI","name":"Zeeker","color":"greenLight2"}]}}} |
| Notes | `fldRfSYet5GLHPtle` | multilineText |  |  |
| DailyReports | `fldHnDXLSj7v0F5Jp` | singleLineText |  |  |
| Table 7 | `fldvdEDSPzKFTJqVZ` | multipleRecordLinks |  | {"linkedTableId":"tblEPkLKKt2D4UIqU","isReversed":false,"prefersSingleRecordLink":false,"inverseLinkFieldId":"fld12zUXISpzDsim7"} |
| Calculation | `fld8TrPfkyCBowWaa` | formula | Filters groups with more than one record in the 'Scans' field. | {"isValid":true,"formula":"IF(COUNTA({fldBZpM5iLEsWe04b}) > 1, TRUE(), FALSE())","referencedFieldIds":["fldBZpM5iLEsWe04b"],"result":{"type":"number","options":{"precision":0}}} |
| Table 10 | `fldSVw8K4lUWHG8o0` | singleLineText |  |  |
| Polish 2 | `fldrLnrolgr6CnPOg` | singleLineText |  |  |

## Table: Scans

**ID:** `tbl9UAOJQRWv9k1Y0`

### Fields

| Name | ID | Type | Description | Options |
|------|----|----|-------------|--------|
| ScanID | `fld1RlzvBPoTgklIy` | autoNumber |  |  |
| LicensePlate | `fldg5alzomE8LHDHf` | multipleLookupValues |  | {"isValid":true,"recordLinkFieldId":"fld77NVrjBEIVtYyW","fieldIdInLinkedTable":"fldU3bHOICNVolEOP","result":{"type":"singleLineText"}} |
| Timestamp | `fldJGUzwfe5sy9OR2` | dateTime | Date and time of the scan | {"dateFormat":{"name":"iso","format":"YYYY-MM-DD"},"timeFormat":{"name":"12hour","format":"h:mma"},"timeZone":"client"} |
| WorkerName | `fldMzixa6FrBmZgxm` | multipleLookupValues |  | {"isValid":true,"recordLinkFieldId":"fldfSmWzNbbfYwu3u","fieldIdInLinkedTable":"fldBi6qCZRCGteGc4","result":{"type":"singleLineText"}} |
| Worker Role | `fldS4rWsqYmsEO3bu` | multipleLookupValues |  | {"isValid":true,"recordLinkFieldId":"fldfSmWzNbbfYwu3u","fieldIdInLinkedTable":"fldIEONuTX5LRCPB2","result":{"type":"singleLineText"}} |
| Photos | `fldpScbzmXa8c2h2r` | multipleAttachments |  | {"isReversed":true} |
| CleanGlue | `fldwJTC1AZFuMM20D` | checkbox | Отдирание клея и наклеек<br> | {"icon":"check","color":"greenBright"} |
| ReturnCleaning | `fldwaDdoUCpgPD875` | checkbox | Повторная мойка<br>  | {"icon":"check","color":"greenBright"} |
| Total scans | `fldOLLfWLa7suHtg5` | multipleLookupValues |  | {"isValid":true,"recordLinkFieldId":"fld77NVrjBEIVtYyW","fieldIdInLinkedTable":"fldCOskkL0fnfv1y1","result":{"type":"number","options":{"precision":0}}} |
| 🧼 Cleaning Price | `fld4D14FfN5fsyxMI` | formula | Calculates the cleaning price based on the status of cleanGlue and ReturnCleaning checkboxes. | {"isValid":true,"formula":"IF(AND({fldwJTC1AZFuMM20D}, {fldwaDdoUCpgPD875}), ERROR(), IF({fldwJTC1AZFuMM20D}, 145, IF({fldwaDdoUCpgPD875}, 50, 70)))","referencedFieldIds":["fldwJTC1AZFuMM20D","fldwaDdoUCpgPD875"],"result":{"type":"singleLineText"}} |
| Vehicle | `fld77NVrjBEIVtYyW` | multipleRecordLinks |  | {"linkedTableId":"tbl7rl82Y64bEuxTQ","isReversed":false,"prefersSingleRecordLink":true,"inverseLinkFieldId":"fldBZpM5iLEsWe04b"} |
| Worker | `fldfSmWzNbbfYwu3u` | multipleRecordLinks |  | {"linkedTableId":"tblC0qoL9psk68IqJ","isReversed":false,"prefersSingleRecordLink":true,"inverseLinkFieldId":"fldBFfqBXJW1CnpuY"} |
| Location | `fldHEJGIeGj1WmLUb` | multipleLookupValues |  | {"isValid":true,"recordLinkFieldId":"fldfSmWzNbbfYwu3u","fieldIdInLinkedTable":"fldZkgab9LzncOZWZ","result":{"type":"singleSelect","options":{"choices":[{"id":"selt7A7u38r9gUJ1D","name":"Tesla","color":"blueLight2"},{"id":"selFSG8jwbGWeQAHn","name":"Lubinsky 1","color":"cyanLight2"},{"id":"sel99IKLWhUc63C11","name":"Lubinsky 2","color":"tealLight2"},{"id":"seltCnZVa2XqtK3NI","name":"Zeeker","color":"greenLight2"}]}}} |
| Notes | `fld4qfCPmtVqKyEEU` | multilineText |  |  |
| Make (from Vehicle) | `fldES5nH33AsHuQ6V` | multipleLookupValues |  | {"isValid":true,"recordLinkFieldId":"fld77NVrjBEIVtYyW","fieldIdInLinkedTable":"fldhyrMNSyBlZH90b","result":{"type":"singleLineText"}} |

## Table: CarDryers

**ID:** `tblEPkLKKt2D4UIqU`

### Fields

| Name | ID | Type | Description | Options |
|------|----|----|-------------|--------|
| workId | `fldda8BrILuaoTyBf` | autoNumber |  |  |
| LicensePlate (from Vehicles) | `fldTdEtpDNrQKXBG5` | multipleLookupValues |  | {"isValid":true,"recordLinkFieldId":"fld12zUXISpzDsim7","fieldIdInLinkedTable":"fldU3bHOICNVolEOP","result":{"type":"singleLineText"}} |
| Name (from Workers) | `fldUbYPzYrwrpkHC8` | multipleLookupValues |  | {"isValid":true,"recordLinkFieldId":"fldr2p5nE8qh8Arch","fieldIdInLinkedTable":"fldBi6qCZRCGteGc4","result":{"type":"singleLineText"}} |
| Work Started | `fldSlyQrIqvjqqXjI` | dateTime |  | {"dateFormat":{"name":"iso","format":"YYYY-MM-DD"},"timeFormat":{"name":"12hour","format":"h:mma"},"timeZone":"client"} |
| Work finished | `fldtjJw2rAyNbM21q` | dateTime |  | {"dateFormat":{"name":"iso","format":"YYYY-MM-DD"},"timeFormat":{"name":"12hour","format":"h:mma"},"timeZone":"client"} |
| Work status | `fld1zIo1OMagr32lw` | singleSelect |  | {"choices":[{"id":"selPCuiVT5EDMJXn1","name":"Started","color":"redBright"},{"id":"selKt5rbDOr2AuNZM","name":"Finished","color":"greenBright"}]} |
| Location (from Workers) | `fld7tUgOmuAvbwkGL` | multipleLookupValues |  | {"isValid":true,"recordLinkFieldId":"fldr2p5nE8qh8Arch","fieldIdInLinkedTable":"fldZkgab9LzncOZWZ","result":{"type":"singleSelect","options":{"choices":[{"id":"selt7A7u38r9gUJ1D","name":"Tesla","color":"blueLight2"},{"id":"selFSG8jwbGWeQAHn","name":"Lubinsky 1","color":"cyanLight2"},{"id":"sel99IKLWhUc63C11","name":"Lubinsky 2","color":"tealLight2"},{"id":"seltCnZVa2XqtK3NI","name":"Zeeker","color":"greenLight2"}]}}} |
| WorkerID (from Workers) | `fldgBoGwD741Su77q` | multipleLookupValues |  | {"isValid":true,"recordLinkFieldId":"fldr2p5nE8qh8Arch","fieldIdInLinkedTable":"fldqeW93mz0JZPrhX","result":{"type":"number","options":{"precision":0}}} |
| VehicleID (from Vehicles) | `fld0vn9fezpYNgHtm` | multipleLookupValues |  | {"isValid":true,"recordLinkFieldId":"fld12zUXISpzDsim7","fieldIdInLinkedTable":"fldqlW7Q0gz87xaCZ","result":{"type":"number","options":{"precision":0}}} |
| Notes | `fldcBfWjQyJOoqAai` | multilineText |  |  |
| Workers | `fldr2p5nE8qh8Arch` | multipleRecordLinks |  | {"linkedTableId":"tblC0qoL9psk68IqJ","isReversed":false,"prefersSingleRecordLink":true,"inverseLinkFieldId":"fld3wpNIiUOy262ZC"} |
| Vehicles | `fld12zUXISpzDsim7` | multipleRecordLinks |  | {"linkedTableId":"tbl7rl82Y64bEuxTQ","isReversed":false,"prefersSingleRecordLink":false,"inverseLinkFieldId":"fldvdEDSPzKFTJqVZ"} |
| Flagged car | `fldhaIwIdbeQlSbdm` | checkbox | If this car was not scanned for the last 7 hours | {"icon":"flag","color":"redBright"} |
| Scans | `fldSlXOHVPLvTUvCF` | multipleLookupValues |  | {"isValid":true,"recordLinkFieldId":"fld12zUXISpzDsim7","fieldIdInLinkedTable":"fldjsorz4ODOHoQoJ","result":{"type":"dateTime","options":{"dateFormat":{"name":"iso","format":"YYYY-MM-DD"},"timeFormat":{"name":"12hour","format":"h:mma"},"timeZone":"client"}}} |

## Table: Polish

**ID:** `tblpNTCIBes9RkLmi`

### Fields

| Name | ID | Type | Description | Options |
|------|----|----|-------------|--------|
| PolishId | `fld6I53DUPtO1sVwE` | autoNumber |  |  |
| LicensePlate (from Vehicles) | `fldv05RQyykIu6DWE` | multipleLookupValues |  | {"isValid":true,"recordLinkFieldId":"fldMae7AhVpYL2jfR","fieldIdInLinkedTable":"fldU3bHOICNVolEOP","result":{"type":"singleLineText"}} |
| Timestamp | `fldm2fkWOH0kOFSCx` | dateTime |  | {"dateFormat":{"name":"iso","format":"YYYY-MM-DD"},"timeFormat":{"name":"12hour","format":"h:mma"},"timeZone":"client"} |
| Services | `fldZuQttR2GzlaEkN` | singleSelect |  | {"choices":[{"id":"selu2qsO32P9rgVxR","name":"HalfPolish","color":"blueLight2"},{"id":"sellx7ITDv9O08gm7","name":"FullPolish","color":"cyanLight2"},{"id":"sellYkBqdHrcxHxMa","name":"Wash","color":"tealLight2"},{"id":"selRYlRPO6wlZtbLD","name":"Shlaif","color":"greenLight2"}]} |
| Photos | `fldDAauquEXLjzZUu` | multipleAttachments |  | {"isReversed":false} |
| WorkerName | `fld56o3lYsVNeSJTG` | multipleLookupValues |  | {"isValid":true,"recordLinkFieldId":"fldl09Do7NCt4sjmQ","fieldIdInLinkedTable":"fldBi6qCZRCGteGc4","result":{"type":"singleLineText"}} |
| Vehicle | `fldMae7AhVpYL2jfR` | multipleRecordLinks |  | {"linkedTableId":"tbl7rl82Y64bEuxTQ","isReversed":false,"prefersSingleRecordLink":false,"inverseLinkFieldId":"fldRLFfChzrhvyPuc"} |
| Worker | `fldl09Do7NCt4sjmQ` | multipleRecordLinks |  | {"linkedTableId":"tblC0qoL9psk68IqJ","isReversed":false,"prefersSingleRecordLink":false,"inverseLinkFieldId":"flddQOmpveaPje8WM"} |

## Table: Locations

**ID:** `tblwgQwZ2Qs6q21a0`

### Fields

| Name | ID | Type | Description | Options |
|------|----|----|-------------|--------|
| LocationID | `flddFcAmCCRZAwzFx` | singleLineText |  |  |
| Name | `fldFiWpr8zCC3KYBH` | singleLineText |  |  |
| Address | `fldrfmoSURhIjP5Jr` | singleLineText |  |  |
| City | `fldrk9v1uPceTmura` | singleLineText |  |  |
| State | `fldHijIddlutQkM8H` | singleLineText |  |  |
| Zip Code | `fldKaPprtTDHnnYUs` | singleLineText |  |  |

## Table: DailySummary

**ID:** `tblrGzPkfiKUO2cBM`

### Fields

| Name | ID | Type | Description | Options |
|------|----|----|-------------|--------|
| Name | `fld5XFhbAmGLZbKFU` | autoNumber |  |  |
| Date | `fldLvXhPwoDvbr5ng` | date |  | {"dateFormat":{"name":"iso","format":"YYYY-MM-DD"}} |
| NormalWash | `fldhudzpyLJERcnfm` | number |  | {"precision":0} |
| AdditionalCleaning | `fldADKwtUf3TxzlGt` | number |  | {"precision":0} |
| LightWash | `fld8vGcEANj9nqfUg` | number |  | {"precision":0} |
| TotalDryed | `fldcIrDiTC6lFYju2` | number |  | {"precision":0} |
| TotalPolished | `fldnHp9iLUxIXyqOX` | number |  | {"precision":0} |
| FullPolish | `fldeiSGQrz9HHEpnF` | number |  | {"precision":0} |
| HalfPolish | `fldA9Pvd0DOBlbCcK` | number |  | {"precision":0} |
| Shlaif | `fld3JWvVqqkiu6Mv7` | number |  | {"precision":0} |
| TotalWashed | `fldB0udaDMIQJpnMw` | number |  | {"precision":0} |
| TotalRevenue | `fldVPvx6g0LqhvfLA` | currency |  | {"precision":2,"symbol":"₪"} |

## Table: MonthlySummary

**ID:** `tbltcTNSXEYKqgaH0`

### Fields

| Name | ID | Type | Description | Options |
|------|----|----|-------------|--------|
| Name | `fld7tZfJiIUBBpIL8` | autoNumber |  |  |
| Month | `fldN1hfneKRlNF3tu` | date |  | {"dateFormat":{"name":"local","format":"l"}} |
| TotalWashed | `fldJwp3cnMuxZrA0b` | number |  | {"precision":0} |
| NormalWash | `fldj0xxXg7XutqllA` | number |  | {"precision":0} |
| AdditionalCleaning | `fldC94u1CBhJ9NjMH` | number |  | {"precision":0} |
| LightWash | `flda10aci9xZZEd0u` | number |  | {"precision":0} |
| TotalDryed | `fldeeLBQBYkbhchAg` | number |  | {"precision":0} |
| TotalPolished | `fldpdJ7QtgLyzMoUb` | number |  | {"precision":0} |
| FullPolish | `fldgOcEo9VnxjSntT` | number |  | {"precision":0} |
| HalfPolish | `fldCF9tLIZ2rXpAiY` | number |  | {"precision":0} |
| TotalRevenue | `fldXlPvEYmZgTJdRO` | currency |  | {"precision":2,"symbol":"₪"} |
| LicensePlatesList | `fldTtK3V1yD5qYVmw` | multilineText |  |  |
| Shlaif | `fldjKjqlBBNs3OHWz` | number |  | {"precision":0} |

