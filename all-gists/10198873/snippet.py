import random
girls = '''Júlia Sophia Isabella Manuela Giovanna Alice Laura 
    Luiza Beatriz Mariana Yasmin Gabriela Rafaela Isabelle Lara 
    Letícia Valentina Nicole Sarah Vitória Isadora Lívia Helena 
    Lorena Clara Larissa Emanuelly Heloisa Marina Melissa Gabrielly 
    Eduarda Rebeca Amanda Alícia Bianca Lavínia Fernanda Ester 
    Carolina Emily Cecília Pietra Milena Marcela Laís Natália
    Maria Bruna Camila Luana Catarina Olivia Agatha Mirella
    Sophie Stella Stefany Isabel Kamilly Elisa Luna Eloá Joana
    Mariane Bárbara Juliana Rayssa Alana Caroline Brenda Evelyn
    Débora Raquel Maitê Ana Nina Hadassa Antonella Jennifer
    Betina Mariah Sabrina'''.split()
girls.sort()
print (' '.join(girls))
secret = random.choice(girls)
guess = ''
while guess != secret:
    guess = input('Guess: ')
    if guess == secret:
        print ('You win!')
    elif guess > secret:
        print ('High')
    else:
        print ('Low')
print ('End of the game!')