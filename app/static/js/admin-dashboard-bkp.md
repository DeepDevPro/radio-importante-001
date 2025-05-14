// Seleciona os botões das abas e os conteúdos correspondentes
const tabs = document.querySelectorAll(".tab");
const abas = document.querySelectorAll(".aba");

tabs.forEach((tab, index) => {
	tab.addEventListener("click", () => {
		// Remove classe 'active' de todas as abas e botões
		tabs.forEach(t => t.classList.remove("active"));
		abas.forEach(a => a.classList.remove("active"));
	
		// Ativa a aba e o botão clicando
		tab.classList.add("active");
		abas[index].classList.add("active");
	});
});

// Limite máximo por imagem: 25MB
const MAX_FILE_SIZE_MB = 25;

// Seleciona o formulário de upload
const formImagem = document.getElementById("form-upload-imagem");
const inputImagem = document.getElementById("input-imagem");

formImagem.addEventListener("submit", function (e) {
	const arquivos = inputImagem.files;

	for (let i = 0; i < arquivos.length; i++) {
		const arquivo = arquivos[i];
		const tamanhoMB = arquivo.size / (1024 * 1024);

		if (tamanhoMB > MAX_FILE_SIZE_MB) {
			e.preventDefault(); // Impede o envio
			alert(`O arquivo "${arquivo.name}" tem ${tamanhoMB.toFixed(2)}MB e excede o limite de ${MAX_FILE_SIZE_MB}MB.`);
			return;
		}
	}
});

// Ativar aba via query string, exemplo: ?aba=imagens (isso vai ser usado pra quando o usuário clicar para carregar as fotos o app retorne para a aba imagens no dash do admin ao invez da aba padrao que é músicas)
const params = new URLSearchParams(window.location.search);
const abaInicial = params.get("aba");

if (abaInicial === "imagens") {
	tabs.forEach(t => t.classList.remove("active"));
	abas.forEach(a => a.classList.remove("active"));
  
	tabs[1].classList.add("active");
	abas[1].classList.add("active");
}

