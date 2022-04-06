const fs = require('fs');
const esprima = require('esprima')
const escodegen = require('escodegen')

var inputtext = process.argv[2];
var outputtext = process.argv[3];

var data = fs.readFileSync(inputtext);
var ast = esprima.parseScript(data.toString());
var ast_to_json = JSON.stringify(ast);
fs.writeFileSync(outputtext, ast_to_json);
