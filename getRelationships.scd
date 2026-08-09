(
// birth data
~year = 1976;
~month = 2;
~day = 23;
~hour = 11;
~minute = 55;
~utcOffset = -8; // seattle


~python = "/Users/roya/Documents/roya/SuperCollider/syntony/chart.py";

~cmd = "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 % % % % % % %".format(
	~python,
	~year,
	~month,
	~day,
	~hour,
	~minute,
	~utcOffset
);

~result = ~cmd.unixCmdGetStdOut;


~relationships = File.readAllString(
	"/Users/roya/Documents/roya/SuperCollider/syntony/chart.json"
).interpret;


// data format: name, aspect numerator, aspect denominator, numerator/denominator, orb, angular separation
~birthRelationships = ~relationships[0];
~transitRelationships = ~relationships[1];
~currentRelationships = ~relationships[2];

/*~birthRelationships.postln;
~transitRelationships.postln;
~currentRelationships.postln;*/
)