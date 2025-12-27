// Buat connector JS
const { PythonShell } = require('python-shell');

export default function runQuery(query) {
    let options = {
        args: [query]
    };
    
    PythonShell.run('script.py', options).then(messages => {
    // messages is an array of responses printed from python
    console.log('Finished:', messages);
    });
}