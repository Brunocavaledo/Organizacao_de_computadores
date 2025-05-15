from enum import Enum


class InstrType(Enum):
    R = 1
    I = 2
    J = 3


class Instruction:

    def __init__(self, bits: str) -> None:
        self.bits = bits
        self.opcode = int(bits[:6], 2)
        self.type = InstrType.R if self.opcode == 0 else \
                    InstrType.J if self.opcode == 2 or self.opcode == 3 else InstrType.I
        self.fields = self.get_fields(self.bits, self.type, self.opcode)
        self.name = MIPSDecoder.OPCODES.get(self.opcode, MIPSDecoder.FUNCTIONS.get(self.fields.get('funct', 0), "Desconhecido"))[0]
        self.mnemonic = self.get_mnemonic(self.fields, self.type)
        print(f' Formato mnemonico: {self.mnemonic}')

    def __str__(self) -> str:
        return self.mnemonic

    @staticmethod
    def get_fields(bits: str, type: InstrType, opcode: int) -> dict:
        #campo1 recebe o tipo de instrução:R, J ou I
        campo1 = "R" if type == InstrType.R else "J" if type == InstrType.J else "I"

        #Criação de um dicionário chamado campos
        campos = {}
        # esses comandos abaixo definem o intervalo dos 32 bits que devo "pegar"
        # int(bits[<inicio>:<fim>], 2), "início" dita o índice do primeiro elemento,
        # "fim" dita o último elemento, mas não o inclui. E 2 determina que isso vai ser convertido em binário.
        # dessa forma separo cada parte que é equivalente a cada informação como rs rd rt e etc
        if campo1 == "R":
            campos = {
                "opcode": opcode,#primeiros 6 bits
                "rs": int(bits[6:11], 2),#do sétimo bit ao décimo bit
                "rt": int(bits[11:16], 2),#do bit 11 ao 15
                "rd": int(bits[16:21], 2),#do bit 16 ao 20
                "shamt": int(bits[21:26], 2),#do bit 21 ao bit 25
                "funct": int(bits[26:32], 2),#do bit 26 até o último
            }
        elif campo1 == "I":
            campos = {
                "opcode": opcode,#primeiros 6 bits
                "rs": int(bits[6:11], 2),#do bit 6 ao 10
                "rt": int(bits[11:16], 2),#do bit 11 ao 15
                "immediate": int(bits[16:32], 2),#do bit 16 ao bit 32
            }
        elif campo1 == "J":
            campos = {
                "opcode": opcode,#primeiros 6 bits
                "address": int(bits[6:32], 2),# nesse caso o endereço de 26 bits vai do sexto bit  até o final dos 32 bits.
            }
        #Devolve as informação já mais ajeitada para cada tipo de caso:
        return campos

    @staticmethod
    def get_mnemonic(fields: dict, type: InstrType) -> str:
        if type == InstrType.R:
            funct = fields.get('funct')
            nome_instrucao = MIPSDecoder.FUNCTIONS.get(funct, "Desconhecido")#acha qual a função e se não tiver retorna "desconhecido"

            rd = MIPSDecoder.get_register_name(fields.get('rd'))
            rs = MIPSDecoder.get_register_name(fields.get('rs'))
            rt = MIPSDecoder.get_register_name(fields.get('rt'))
            shamt = fields.get('shamt')

            # Busca o formato correto de mnemônico e substitui os placeholders
            formato = MIPSDecoder.MNEMONIC_FORMATS.get(nome_instrucao, "<instr> <rd>, <rs>, <rt>")#busca lá no dicionario que criei o jeitao da instrução

            # aqui ele retorna já substituindo
            return formato.replace("<instr>", nome_instrucao) \
                .replace("<rd>", rd) \
                .replace("<rs>", rs) \
                .replace("<rt>", rt) \
                .replace("<shamt>", str(shamt))
        #abaixo são as condicionais para os tipos J ou I que são mais faceis
        elif type == InstrType.I:
            rs = MIPSDecoder.get_register_name(fields.get('rs'))
            rt = MIPSDecoder.get_register_name(fields.get('rt'))
            immediate = fields.get('immediate')
            nome_instrucao, formato = MIPSDecoder.OPCODES.get(fields['opcode'], ("Desconhecido", ""))
            return formato.replace("<instr>", nome_instrucao) \
                .replace("<rs>", rs) \
                .replace("<rt>", rt) \
                .replace("<imm>", str(immediate))

        elif type == InstrType.J:
            address = fields.get('address')
            nome_instrucao, formato = MIPSDecoder.OPCODES.get(fields['opcode'], ("Desconhecido", ""))
            return formato.replace("<instr>", nome_instrucao) \
                .replace("<label>", str(address))
        #se não bater com nada ate agora então ele retorna "desconhecido"
        else:
            return "Desconhecido"

class MIPSDecoder:

    REGISTERS = {
        0: '$zero',
        1: '$at',
        2: '$v0',
        3: '$v1',
        4: '$a0',
        5: '$a1',
        6: '$a2',
        7: '$a3',
        8: '$t0',
        9: '$t1',
        10: '$t2',
        11: '$t3',
        12: '$t4',
        13: '$t5',
        14: '$t6',
        15: '$t7',
        16: '$s0',
        17: '$s1',
        18: '$s2',
        19: '$s3',
        20: '$s4',
        21: '$s5',
        22: '$s6',
        23: '$s7',
        24: '$t8',
        25: '$t9',
        26: '$k0',
        27: '$k1',
        28: '$gp',
        29: '$sp',
        30: '$s8',
        31: '$ra'
    }

    OPCODES = {
        0b000000: ('[R-Type]', ''),  # Todas as instruções do tipo R são identificadas pelo campo 'funct'
        # I-Type Instructions
        0b001000: ('addi', '<instr> <rt>, <rs>, <imm>'),  # addi rt, rs, immediate
        0b001001: ('addiu', '<instr> <rt>, <rs>, <imm>'),  # addiu rt, rs, immediate
        0b001100: ('andi', '<instr> <rt>, <rs>, <imm>'),  # andi rt, rs, immediate
        0b000100: ('beq', '<instr> <rs>, <rt>, <label>'),  # beq rs, rt, label
        0b000001: ('bgez', '<instr> <rs>, <label>'),  # bgez rs, label
        0b000111: ('bgtz', '<instr> <rs>, <label>'),  # bgtz rs, label
        0b000110: ('blez', '<instr> <rs>, <label>'),  # blez rs, label
        # 0b000001: ('bltz', '<instr> <rs>, <label>'),  # bltz rs, label
        0b000101: ('bne', '<instr> <rs>, <rt>, <label>'),  # bne rs, rt, label
        0b100000: ('lb', '<instr> <rt>, <imm>(<rs>)'),  # lb rt, immediate(rs)
        0b100100: ('lbu', '<instr> <rt>, <imm>(<rs>)'),  # lbu rt, immediate(rs)
        0b100001: ('lh', '<instr> <rt>, <imm>(<rs>)'),  # lh rt, immediate(rs)
        0b100101: ('lhu', '<instr> <rt>, <imm>(<rs>)'),  # lhu rt, immediate(rs)
        0b001111: ('lui', '<instr> <rt>, <imm>'),  # lui rt, immediate
        0b100011: ('lw', '<instr> <rt>, <imm>(<rs>)'),  # lw rt, immediate(rs)
        0b110001: ('lwc1', '<instr> <rt>, <imm>(<rs>)'),  # lwc1 rt, immediate(rs)
        0b001101: ('ori', '<instr> <rt>, <rs>, <imm>'),  # ori rt, rs, immediate
        0b101000: ('sb', '<instr> <rt>, <imm>(<rs>)'),  # sb rt, immediate(rs)
        0b001010: ('slti', '<instr> <rt>, <rs>, <imm>'),  # slti rt, rs, immediate
        0b001011: ('sltiu', '<instr> <rt>, <rs>, <imm>'),  # sltiu rt, rs, immediate
        0b101001: ('sh', '<instr> <rt>, <imm>(<rs>)'),  # sh rt, immediate(rs)
        0b101011: ('sw', '<instr> <rt>, <imm>(<rs>)'),  # sw rt, immediate(rs)
        0b111001: ('swc1', '<instr> <rt>, <imm>(<rs>)'),  # swc1 rt, immediate(rs)
        0b001110: ('xori', '<instr> <rt>, <rs>, <imm>'),  # xori rt, rs, immediate
        # J-Type Instructions
        0b000010: ('j', '<instr> <label>'),  # j label
        0b000011: ('jal', '<instr> <label>')  # jal label
    }

    FUNCTIONS = {
        # R-Type Instructions
        0b100000: 'add',	            # add rd, rs, rt
        0b100001: 'addu',	            # addu rd, rs, rt
        0b100100: 'and',	            # and rd, rs, rt
        0b001101: 'break',	            # break
        0b011010: 'div',	            # div rs, rt
        0b011011: 'divu',	            # divu rs, rt
        0b001001: 'jalr',	            # jalr rd, rs
        0b001000: 'jr',	                # jr rs
        0b010000: 'mfhi',	            # mfhi rd
        0b010010: 'mflo',	            # mflo rd
        0b010001: 'mthi',	            # mthi rs
        0b010011: 'mtlo',	            # mtlo rs
        0b011000: 'mult',	            # mult rs, rt
        0b011001: 'multu',	            # multu rs, rt
        0b100111: 'nor',	            # nor rd, rs, rt
        0b100101: 'or',	                # or rd, rs, rt
        0b000000: 'sll',	            # sll rd, rt, sa
        0b000100: 'sllv',	            # sllv rd, rt, rs
        0b101010: 'slt',	            # slt rd, rs, rt
        0b101011: 'sltu',	            # sltu rd, rs, rt
        0b000011: 'sra',	            # sra rd, rt, sa
        0b000111: 'srav',	            # srav rd, rt, rs
        0b000010: 'srl',                # srl rd, rt, sa
        0b000110: 'srlv',	            # srlv rd, rt, rs
        0b100010: 'sub',	            # sub rd, rs, rt
        0b100011: 'subu',	            # subu rd, rs, rt
        0b001100: 'syscall',	        # syscall
        0b100110: 'xor',	            # xor rd, rs, rt
    }

    # Dicionario para as instruções do tipo R diferentes do padrão normal
    # Mapeamento dos formatos de mnemônico
    MNEMONIC_FORMATS = {
        'jr': '<instr> <rs>',
        'jalr': '<instr> <rd>, <rs>',
        'mfhi': '<instr> <rd>',
        'mflo': '<instr> <rd>',
        'mthi': '<instr> <rs>',
        'mtlo': '<instr> <rs>',
        'mult': '<instr> <rs>, <rt>',
        'multu': '<instr> <rs>, <rt>',
        'div': '<instr> <rs>, <rt>',
        'divu': '<instr> <rs>, <rt>',
        'sll': '<instr> <rd>, <rt>, <shamt>',
        'sra': '<instr> <rd>, <rt>, <shamt>',
        'srl': '<instr> <rd>, <rt>, <shamt>',
        'sllv': '<instr> <rd>, <rt>, <rs>',
        'srlv': '<instr> <rd>, <rt>, <rs>',
        'srav': '<instr> <rd>, <rt>, <rs>',
        'syscall': '<instr>',
        'break': '<instr>',
        'movn': '<instr> <rd>, <rs>, <rt>',
        'movz': '<instr> <rd>, <rs>, <rt>',
        'clo': '<instr> <rd>, <rs>',
        'clz': '<instr> <rd>, <rs>',
        'seb': '<instr> <rd>, <rt>',
        'seh': '<instr> <rd>, <rt>'
    }

    def parse_instruction(self, bits: str) -> Instruction:
        return Instruction(bits)

    def decode_instruction(self, instr) -> dict: #Isso aqui, só por Deus viu...
        # Implemente aqui...
        # Este método deve retornar um dicionário com os sinais de controle da instrução
        # { RegDst, Branch, MemRead, MemWrite, MemToReg, ALUSrc, RegWrite }. Exemplo:
        return {
            'ALUSrc': None,
            'Branch': None,
            'MemRead': None,
            'MemToReg': None,
            'MemWrite': None,
            'RegDst': None,
            'RegWrite': None
        }

    @staticmethod
    def get_register_name(register_index: int) -> str:
        return MIPSDecoder.REGISTERS[register_index]

    @staticmethod
    def get_register_index(register_name: str) -> int:
        inv_map = { v: k for k, v in MIPSDecoder.REGISTERS.items() }
        return inv_map[register_name]


def parse_int(num_str: str) -> int:
    num_str = num_str.lower()
    base = 2 if num_str.startswith('0b') else 8 if num_str.startswith('0o') else \
           16 if num_str.startswith('0x') else 10
    return int(num_str, base)


def print_output(instr: Instruction, signals: dict) -> None:
    if instr.type == InstrType.R:
        print(f'Instrução: {MIPSDecoder.FUNCTIONS.get(instr.fields.get("funct", 0), "Desconhecido")}')
    else:
        print(f'Instrução: {instr.name}')
    print(f'- Tipo: {instr.type.name}')
    print(f'- Campos:')
    for field, value in instr.fields.items():
        if field == 'opcode' and instr.opcode != 0:
            print(f'\t{field}: {value} ({MIPSDecoder.OPCODES[value][0]})')
        elif field == 'funct':
            print(f'\t{field}: {value} ({MIPSDecoder.FUNCTIONS[value]})')
        elif field == 'rs' or field == 'rt' or field == 'rd':
            print(f'\t{field}: {value} ({MIPSDecoder.REGISTERS[value]})')
        else:
            print(f'\t{field}: {value}')
    print(f'- Sinais de controle:')
    for signal, value in signals.items():
        print(f'\t{signal}: {value}')


def main():

    decoder = MIPSDecoder()
    print("--- [Decodificador de instruções MIPS] ---")
    while True:
        print("Digite o [inteiro] da instrução | [''] para sair:", end=' ')
        input_value = input().strip()
        if not input_value:
            break
        instr = decoder.parse_instruction(f'{parse_int(input_value):032b}')
        signals = decoder.decode_instruction(instr)
        print_output(instr, signals)


if __name__ == '__main__':
    main()

    #PARA TESTAR O CÓDIGO:
    # # Instruções do tipo R (funct define a operação)
    # instr_r =
    #     "0b00000000001000000000000000001000",  # jr $1
    #     "0b00000000001000100001100000100000",  # add $3, $1, $2
    #     "0b00000000001000100001100000100001",  # addu $3, $1, $2
    #     "0b00000000001000100001100000100100",  # and $3, $1, $2
    #     "0b00000000001000000000000000011000",  # mult $1, $2
    #     "0b00000000001000100001100000000000",  # sll $3, $2, 0
    #     "0b00000000001000100001100000000011",  # sra $3, $2, 3
    #     "0b00000000000000000000000000001100",  # syscall
    #
    # # Instruções do tipo I (opcode define a operação)
    # instr_i =
    #     "0b10010000001000100000000000000100",  # lbu $2, 4($1)
    #     "0b00100000001000100000000000000001",  # addi $3, $1, 1
    #     "0b00100100001000010000000000000010",  # addiu $1, $1, 2
    #     "0b00110000001000100000000000001111",  # andi $3, $1, 15
    #     "0b00010000001000100000000000000100",  # beq $1, $2, 4
    #     "0b10001100001000110000000000000100",  # lw $3, 4($1)
    #     "0b10101100001000100000000000001000",  # sw $3, 8($1)
    #
    # # Instruções do tipo J (opcode define a operação)
    # instr_j =
    #     "0b00001000000000000000000000000100",  # j 4
    #     "0b00001100000000000000000000001000",  # jal 8
    #
