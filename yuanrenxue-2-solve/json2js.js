const fs = require('fs');
const esprima = require('esprima')
const escodegen = require('escodegen')

var inputtext = process.argv[2];
var outputtext = process.argv[3];

var data = fs.readFileSync(inputtext);
var ast = JSON.parse(data.toString());
var code = escodegen.generate(ast, {
    format: {
        compact: true,
        escapeless: true
    }
});
fs.writeFileSync(outputtext, code);
