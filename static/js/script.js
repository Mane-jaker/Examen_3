function analyzeCode() {
    const code = document.getElementById('code-input').value;
    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: code })
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('results').textContent = data.error_2 ? data.error_2 : data.parse_result;
            document.getElementById('results-2').textContent = data.error ? data.error : data.parse_result;
            const tableBody = document.getElementById('token-table-body');
            tableBody.innerHTML = '';  // Limpiar la tabla antes de añadir nuevas filas
            let totalPR = 0, totalID = 0, totalSymbols = 0, totalError = 0, totalNumber = 0;

            data.tokens_list.forEach(token => {
                const row = tableBody.insertRow();

                // Celda para el valor del token
                const tokenCell = row.insertCell();
                tokenCell.textContent = token.value;
                tokenCell.className = 'border border-black px-4 py-2';

                // Celda para PR
                const prCell = row.insertCell();
                prCell.textContent = (['FOR', 'IF', 'DO', 'WHILE', 'ELSE', 'PROGRAMA', 'READ', 'INT', 'FLOAT', 'STRING', 'SYSTEM','OUT','PRINTLN'].includes(token.type)) ? 'X' : '';
                prCell.className = 'border border-black px-4 py-2 text-center';
                if (['FOR', 'IF', 'DO', 'WHILE', 'ELSE', 'PROGRAMA', 'READ', 'INT', 'FLOAT', 'STRING', 'SYSTEM','OUT','PRINTLN'].includes(token.type)) totalPR++;

                const numberCell = row.insertCell();
                numberCell.textContent = (['NUMBER'].includes(token.type)) ? 'X' : '';
                numberCell.className = 'border border-black px-4 py-2 text-center';
                if (['NUMBER'].includes(token.type)) totalNumber++;

                // Celda para ID
                const idCell = row.insertCell();
                idCell.textContent = (token.type === 'ID' || token.type === 'TEXT') ? 'X' : '';
                idCell.className = 'border border-black px-4 py-2 text-center';
                if (token.type === 'ID' || token.type === 'TEXT') totalID++;

                // Celda para Símbolo
                const symbolCell = row.insertCell();
                symbolCell.textContent = (token.type === 'LPAREN' || token.type === 'RPAREN' || token.type === 'SEMICOLON' || token.type === 'COMMA' || token.type === 'LBRACE' || token.type === 'RBRACE'  || token.type === 'LTE'|| token.type === 'PLUS' || token.type === 'DOT' || token.type === 'ASSIGN' || token.type === 'GT' ) ? 'X' : '';
                symbolCell.className = 'border border-black px-4 py-2 text-center';
                if (token.type === 'LPAREN' || token.type === 'RPAREN' || token.type === 'SEMICOLON' || token.type === 'COMMA' || token.type === 'LBRACE' || token.type === 'RBRACE' || token.type === 'LTE'|| token.type === 'PLUS' || token.type === 'DOT' || token.type === 'ASSIGN' || token.type === 'GT' ) totalSymbols++;

                const errorCell = row.insertCell();
                errorCell.textContent = (token.type === 'ERROR') ? 'X' : '';
                errorCell.className = 'border border-black px-4 py-2 text-center';
                if (token.type === 'ERROR') totalError++;
            });

            // Añadir fila de totales al final
            const totalRow = tableBody.insertRow();
            totalRow.insertCell().textContent = "Total";
            totalRow.insertCell().textContent = totalPR;
            totalRow.insertCell().textContent = totalNumber;
            totalRow.insertCell().textContent = totalID;
            totalRow.insertCell().textContent = totalSymbols;
            totalRow.insertCell().textContent = totalError;

            totalRow.cells[0].className = 'border border-black px-4 py-2 font-bold';
            totalRow.cells[1].className = 'border border-black px-4 py-2 text-center';
            totalRow.cells[2].className = 'border border-black px-4 py-2 text-center';
            totalRow.cells[3].className = 'border border-black px-4 py-2 text-center';
            totalRow.cells[4].className = 'border border-black px-4 py-2 text-center';
            totalRow.cells[5].className = 'border border-black px-4 py-2 text-center';
        })
        .catch(error => console.error('Error:', error));
}