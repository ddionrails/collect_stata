/*
This do-file creates a test dataset in stata for collect_stata.
*/
clear

// Generate Variables
gen TESTCAT = ""
gen TESTSTRING = ""
gen TESTNUMBER = ""
gen TESTOTHER = ""

// Create Testdata
local TESTCAT = "-1 -1 .b 2 1 . 1 2 1 2 2 1 1 2 2"
local TESTSTRING = ". a b .a . c . .b . d e f f f g"
local TESTNUMBER = "-1 .a -2 5 10 10 15 100 10 2 -1 3 4 5 6"
local TESTOTHER = "-1 a -2 5 b . 15 x 2 3 b 1 2 y z"

local data = "TESTCAT TESTSTRING TESTNUMBER TESTOTHER"

// Set 15 Observations
set obs 15

// Fill each Variable with its values
foreach variable of local data {
	local i = 1
	foreach value of local `variable' {
		replace `variable' = "`value'" in `i'
		local ++i
	}
}

// Change Varlabels
label var TESTCAT "label for testcat"
label var TESTSTRING "label for teststring"
label var TESTNUMBER "label for testnumber"
label var TESTOTHER "label for other test type"

// Convert TESTCAT and TESTNUMBER to byte
destring TESTCAT, replace
destring TESTNUMBER, replace

// Define labels for values of the categorical variable
label define catvalues -1 "missing" 1 "a" 2 "b"
label value TESTCAT catvalues
