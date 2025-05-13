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
        self.fields = self.get_fields(self.bits, self.type)
        self.name = MIPSDecoder.OPCODES.get(self.opcode, MIPSDecoder.FUNCTIONS.get(self.fields.get('funct', 0), "Desconhecido"))
        self.mnemonic = self.get_mnemonic(self.fields, self.type)

    def __str__(self) -> str:
        return self.mnemonic

    @staticmethod
    def get_fields(bits: str, type: InstrType) -> dict:
        # dos 32 bits ele pega do índice 0 ao 5(não incluindo o 6), e converte os bits para decimais
        # com o comando "2" no final e guarda na variável instrução:
        instrucao = int(bits[0:6], 2)
        # define os 3 tipos de instruções baseado no decimal formado logo acima, com essa informação saberei mais pra frente
        # como usar os bits para interpretar direito cada tipo:
        if instrucao == 0:
            campo1 = "R"
        elif instrucao == 2 or instrucao == 3:#2 ou 3 é do tipo J(jump).
            campo1 = "J"
        else:
            campo1 = "I"#se não for de valor 0, 2 ou 3 então todos os outros tipo são do tipo imediato.

        #Condicional para cada tipo de instrução
        campos = {}
        if campo1 == "R":
            #esses comandos abaixo definem o intervalo dos 32 bits que devo "pegar"
            #int(bits[<inicio>:<fim>], 2), "início" dita o índice do primeiro elemento,
            # "fim" dita o último elemento, mas não o inclui. E 2 determina que isso vai ser convertido em binário.
            #dessa forma separo cada parte que é equivalente a cada informação como rs rd rt e etc
            campos = {
                "opcode": instrucao,#primeiros 6 bits
                "rs": int(bits[6:11], 2),#do sétimo bit ao décimo bit
                "rt": int(bits[11:16], 2),#do bit 11 ao 15
                "rd": int(bits[16:21], 2),#do bit 16 ao 20
                "shamt": int(bits[21:26], 2),#do bit 21 ao bit 25
                "funct": int(bits[26:32], 2),#do bit 26 até o último
            }
        elif campo1 == "I":
            campos = {
                "opcode": instrucao,#primeiros 6 bits
                "rs": int(bits[6:11], 2),#do bit 6 ao 10
                "rt": int(bits[11:16], 2),#do bit 11 ao 15
                "immediate": int(bits[16:32], 2),#do bit 16 ao bit 32
            }
        elif campo1 == "J":
            campos = {
                "opcode": instrucao,#primeiros 6 bits
                "address": int(bits[6:32], 2),# nesse caso o endereço de 26 bits vai do sexto bit  até o final dos 32 bits.
            }
        #Devolve as informação já mais ajeitada para cada tipo de caso:
        return campos

    @staticmethod
    def get_mnemonic(fields: dict, type: InstrType) -> str:#esse método vai servir pra acessar o que cada instrução quer dizer
        #Aqui crio condicionais para encaixar na situação certa o tipo de instrução
        if type == InstrType.R:
            #Abaixo eu armazeno cada instrução mips dentro das variáveis respectivas para apresentar elas ao final da execução,
            #essas instruções são acessadas lá na classe MIPSDecoder, tá td la dentro, eu só preciso comparar e
            # encontrar qual tipo de instrução é a que estou recebendo, cada uma delas vai ter suas características próprias
            funct = fields.get('funct')
            rd = MIPSDecoder.get_register_name(fields.get('rd'))
            rs = MIPSDecoder.get_register_name(fields.get('rs'))
            rt = MIPSDecoder.get_register_name(fields.get('rt'))
            return f"{MIPSDecoder.FUNCTIONS[funct]} {rd}, {rs}, {rt}"
        elif type == InstrType.I:
            rs = MIPSDecoder.get_register_name(fields.get('rs'))
            rt = MIPSDecoder.get_register_name(fields.get('rt'))
            immediate = fields.get('immediate')
            return f"{MIPSDecoder.OPCODES[fields['opcode']]} {rs, rt, immediate}"
        elif type == InstrType.J:
            address = fields.get('address') # Usa ".get" para evitar KeyError, se eu usasse instanciamento poderia dar erro, mas com get ele retorna None
            return f"{MIPSDecoder.OPCODES[fields['opcode']]} {address}"
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
        0b000000: '[R-Type]',
        # I-Type Instructions
        0b001000: 'addi',	            # addi rt, rs, immediate
        0b001001: 'addiu',	            # addiu rt, rs, immediate
        0b001100: 'andi',	            # andi rt, rs, immediate
        0b000100: 'beq',	            # beq rs, rt, label
        0b000001: 'bgez', # rt = 00001	# bgez rs, label
        0b000111: 'bgtz', # rt = 00000	# bgtz rs, label
        0b000110: 'blez', # rt = 00000	# blez rs, label
        # 0b000001: 'bltz', # rt = 00000	# bltz rs, label
        0b000101: 'bne',	            # bne rs, rt, label
        0b100000: 'lb',	                # lb rt, immediate(rs)
        0b100100: 'lbu',	            # lbu rt, immediate(rs)
        0b100001: 'lh',	                # lh rt, immediate(rs)
        0b100101: 'lhu',	            # lhu rt, immediate(rs)
        0b001111: 'lui',	            # lui rt, immediate
        0b100011: 'lw',	                # lw rt, immediate(rs)
        0b110001: 'lwc1',	            # lwc1 rt, immediate(rs)
        0b001101: 'ori',	            # ori rt, rs, immediate
        0b101000: 'sb',	                # sb rt, immediate(rs)
        0b001010: 'slti',	            # slti rt, rs, immediate
        0b001011: 'sltiu',	            # sltiu rt, rs, immediate
        0b101001: 'sh',	                # sh rt, immediate(rs)
        0b101011: 'sw',	                # sw rt, immediate(rs)
        0b111001: 'swc1',	            # swc1 rt, immediate(rs)
        0b001110: 'xori',	            # xori rt, rs, immediate
        # J-Type Instructions
        0b000010: 'j',                  # j label
        0b000011: 'jal'                 # jal label
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

    def parse_instruction(self, bits: str) -> Instruction:
        return Instruction(bits)

    def decode_instruction(self, instr) -> dict:
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
    print(f'Instrução: {instr.name}')
    print(f'- Tipo: {instr.type.name}')
    print(f'- Campos:')
    for field, value in instr.fields.items():
        if field == 'opcode' and instr.opcode != 0:
            print(f'\t{field}: {value} ({MIPSDecoder.OPCODES[value]})')
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