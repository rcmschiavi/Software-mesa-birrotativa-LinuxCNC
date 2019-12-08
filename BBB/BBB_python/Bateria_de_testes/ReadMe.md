## Bateria de testes do projeto

Foi necessário gerar uma bateria de testes do projeto, uma vez que não era possível testar durante o desenvolvimento.
Testes separados foram realizados para cada conceito empregado.

### Como utilizar

Para realizar a bateria de testes é necessário executar o arquivo "setup_machine.sh" dentro de cada pasta por meio do comando:

- sudo chmod +x setup_machine.sh
- ./setup_machine.sh

### Estrutura dos testes

- Inspect:
    - no_modbus
        - no_modbus.py
    - plus_modbus
        - plus_modbus.py

- Motion:
    - NO_fanuc
        - NO_gui
            - home
            - jog
            - program
        - plus_gui
            -gui
    - plus_fanuc
        - program


