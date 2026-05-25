let currentStatus = 'Todos';

function formatarData(dateString) {
    if (!dateString) return '-';
    
    console.log("Debug Formatando data:", dateString);
    
    try {
        // Formato esperado: YYYY-MM-DD HH:MM:SS ou YYYY-MM-DD
        const parts = dateString.split(/[- :.]/);
        
        // Caso YYYY-MM-DD
        if (parts.length === 3) {
            return `${parts[2]}/${parts[1]}/${parts[0]}`;
        }
        // Caso YYYY-MM-DD HH:MM:SS
        else if (parts.length >= 5) {
            return `${parts[2]}/${parts[1]}/${parts[0]} ${parts[3]}:${parts[4]}`;
        }
        return dateString;
    } catch (e) {
        console.error("Erro formatando data:", e);
        return dateString;
    }
}

function carregarDevolucoes(termo = '', data = '') {
    let url = `/emprestimo/api/devolucoes?busca=${encodeURIComponent(termo)}&data=${encodeURIComponent(data)}`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('tabelaDevolucoesBody');
            tbody.innerHTML = '';
            
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted">Nenhum registro encontrado.</td></tr>';
                return;
            }
            
            data.forEach(dev => {
                let badgeClass = 'bg-info';
                if (dev.status === 'DEVOLVIDO') badgeClass = 'bg-danger text-white';
                if (dev.status === 'ATIVO') badgeClass = 'bg-success';
                if (dev.status === 'SOLICITADO') badgeClass = 'bg-primary text-white';
                
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${dev.titulo}</td>
                    <td>${dev.usuario}</td>
                    <td><span class="badge ${badgeClass}">${dev.status}</span></td>
                    <td>${formatarData(dev.data_solicitacao)}</td>
                    <td><span class="text-success">${formatarData(dev.data_devolucao)}</span></td>
                `;
                tbody.appendChild(row);
            });
        });
}

// Autocomplete
document.getElementById('buscaDevolucao').addEventListener('input', function() {
    const termo = this.value;
    if (termo.length >= 3) {
        fetch(`/emprestimo/api/autocomplete?q=${encodeURIComponent(termo)}`)
            .then(r => r.json())
            .then(data => {
                const list = document.getElementById('autocompleteList');
                list.innerHTML = '';
                data.forEach(item => {
                    list.innerHTML += `<button class="list-group-item list-group-item-action" onclick="selecionar('${item}')">${item}</button>`;
                });
            });
        carregarDevolucoes(termo, document.getElementById('dataDevolucao').value);
    } else {
        carregarDevolucoes('', document.getElementById('dataDevolucao').value);
    }
});

function selecionar(item) {
    document.getElementById('buscaDevolucao').value = item;
    document.getElementById('autocompleteList').innerHTML = '';
    carregarDevolucoes(item, document.getElementById('dataDevolucao').value);
}

document.getElementById('dataDevolucao').addEventListener('change', () => {
    carregarDevolucoes(document.getElementById('buscaDevolucao').value, document.getElementById('dataDevolucao').value);
});

// Carregar inicial
document.addEventListener('DOMContentLoaded', carregarDevolucoes);
