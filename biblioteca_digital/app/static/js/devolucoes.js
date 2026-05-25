let currentStatus = 'Todos';

function formatarData(dateString) {
    if (!dateString || dateString === 'None' || dateString === '-') return '-';
    
    // Tenta capturar YYYY, MM, DD, HH, MM de strings como '2026-05-24 17:03:03.030899'
    const match = dateString.match(/(\d{4})-(\d{2})-(\d{2})[\sT](\d{2}):(\d{2})/);
    
    if (match) {
        // match[1]: YYYY, [2]: MM, [3]: DD, [4]: HH, [5]: MM
        // Formato solicitado: DD/MM/AA HH:MM
        return `${match[3]}/${match[2]}/${match[1].slice(2)} ${match[4]}:${match[5]}`;
    }
    
    return dateString;
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
