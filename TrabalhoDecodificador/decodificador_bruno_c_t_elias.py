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
        if self.type == InstrType.R:
            self.name = MIPSDecoder.FUNCTIONS.get(self.fields.get('funct', 0), "Desconhecido")#se for R ele pega a parte dos 32bits referente a funct e atribui ao name qual tipo ela é
        else:
            self.name = MIPSDecoder.OPCODES.get(self.opcode, ("Desconhecido", ""))[0] #se for I ou J é mais simples, ele pega a primeira posição

        self.mnemonic = self.get_mnemonic(self.fields, self.type)
        print(f'Formato mnemônico: {self.mnemonic}')# pra imprimir o formato mnemonico da instrução

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
        if type == InstrType.R: # No caso de ser tipo R
            funct = fields.get('funct')
            nome_instrucao = MIPSDecoder.FUNCTIONS.get(funct, "Desconhecido")#acha qual a função e se não tiver retorna "desconhecido"
            # Atribui valores as respectivas variáveis:
            rd = MIPSDecoder.get_register_name(fields.get('rd'))
            rs = MIPSDecoder.get_register_name(fields.get('rs'))
            rt = MIPSDecoder.get_register_name(fields.get('rt'))
            shamt = fields.get('shamt')

            # Busca o formato correto de mnemônico e substitui os placeholders
            formato = MIPSDecoder.MNEMONIC_FORMATS.get(nome_instrucao, "<instr> <rd>, <rs>, <rt>")#busca lá no dicionario que criei o jeitao da instrução

            # aqui ele retorna já substituindo através do método find-replace
            return formato.replace("<instr>", nome_instrucao) \
                .replace("<rd>", rd) \
                .replace("<rs>", rs) \
                .replace("<rt>", rt) \
                .replace("<shamt>", str(shamt))
        #abaixo são as condicionais para os tipos J ou I, que são mais simples
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
            #Retorna com o formato da instrução
            return formato.replace("<instr>", nome_instrucao) \
                .replace("<label>", str(address))
        #se não bater com nada até agora então ele retorna "desconhecido"
        else:
            return "Desconhecido"

class MIPSDecoder: #Dicionário ou mapa
    #Dicionário dos registradores
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
    #Dicionário dos opcodes estilo chave e valor, agora com tuplas
    OPCODES = {
        0b000000: ('R', ''),  # Todas as instruções do tipo R são identificadas pelo campo 'funct'
        # I-Type Instructions
        0b001000: ('addi', '<instr> <rt>, <rs>, <imm>'),  # addi rt, rs, immediate
        0b001001: ('addiu', '<instr> <rt>, <rs>, <imm>'),  # addiu rt, rs, immediate
        0b001100: ('andi', '<instr> <rt>, <rs>, <imm>'),  # andi rt, rs, immediate
        0b000100: ('beq', '<instr> <rs>, <rt>, <label>'),  # beq rs, rt, label
        0b000001: ('bgez', '<instr> <rs>, <label>'),  # bgez rs, label
        0b000111: ('bgtz', '<instr> <rs>, <label>'),  # bgtz rs, label
        0b000110: ('blez', '<instr> <rs>, <label>'),  # blez rs, label
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
    # Dicionário de funções, que são para o tipo R
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

    # Dicionario para as instruções do tipo R diferentes do padrão normal, a partir das Functions a gente parte pra cá.
    # Mapeamento dos formatos de mnemônico usando tuplas para saber qual o jeitão de cada uma
    MNEMONIC_FORMATS = {
        'add': '<instr> <rd>, <rs>, <rt>',
        'addu': '<instr> <rd>, <rs>, <rt>',
        'and': '<instr> <rd>, <rs>, <rt>',
        'break': '<instr>',
        'div': '<instr> <rs>, <rt>',
        'divu': '<instr> <rs>, <rt>',
        'jr': '<instr> <rs>',
        'jalr': '<instr> <rd>, <rs>',
        'mfhi': '<instr> <rd>',
        'mflo': '<instr> <rd>',
        'mthi': '<instr> <rs>',
        'mtlo': '<instr> <rs>',
        'mult': '<instr> <rs>, <rt>',
        'multu': '<instr> <rs>, <rt>',
        'sll': '<instr> <rd>, <rt>, <shamt>',
        'sra': '<instr> <rd>, <rt>, <shamt>',
        'srl': '<instr> <rd>, <rt>, <shamt>',
        'sllv': '<instr> <rd>, <rt>, <rs>',
        'srlv': '<instr> <rd>, <rt>, <rs>',
        'srav': '<instr> <rd>, <rt>, <rs>',
        'slt': '<instr> <rd>, <rs>, <rt>',
        'sltu': '<instr> <rd>, <rs>, <rt>',
        'sub': '<instr> <rd>, <rs>, <rt>',
        'subu': '<instr> <rd>, <rs>, <rt>',
        'syscall': '<instr>',
        'or': '<instr> <rd>, <rs>, <rt>',
        'xor': '<instr> <rd>, <rs>, <rt>',
        'nor': '<instr> <rd>, <rs>, <rt>',
    }

    def parse_instruction(self, bits: str) -> Instruction:
        return Instruction(bits)

    @staticmethod
    def get_sinais_de_controle(instr):

        sinais_de_controle = {
            # tipo R
            'add': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                    'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'addu': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'and': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                    'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'break': {'RegDst': 0, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 0,
                      'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'div': {'RegDst': 0, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 0,
                    'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'divu': {'RegDst': 0, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 0,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'jalr': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 1},
            'jr': {'RegDst': 0, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 0,
                   'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 1},
            'mfhi': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'mflo': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'mthi': {'RegDst': 0, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 0,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'mtlo': {'RegDst': 0, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 0,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'mult': {'RegDst': 0, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 0,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'multu': {'RegDst': 0, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 0,
                      'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'nor': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                    'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'or': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                   'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'sll': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                    'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'sllv': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'sra': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                    'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'srav': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'srl': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                    'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'srlv': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'slt': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                    'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'sltu': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'sub': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                    'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'subu': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'syscall': {'RegDst': 0, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 0,
                        'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'movn': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'movz': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'clo': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                    'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'seb': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                    'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'seh': {'RegDst': 1, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                    'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},

            # Tipo I
            'addi': {'RegDst': 0, 'ALUSrc': 1, 'MemToReg': 0, 'RegWrite': 1,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'addiu': {'RegDst': 0, 'ALUSrc': 1, 'MemToReg': 0, 'RegWrite': 1,
                      'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'andi': {'RegDst': 0, 'ALUSrc': 1, 'MemToReg': 0, 'RegWrite': 1,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'beq': {'RegDst': 0, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 0,
                    'MemRead': 0, 'MemWrite': 0, 'Branch': 1, 'Jump': 0},
            'bne': {'RegDst': 0, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 0,
                    'MemRead': 0, 'MemWrite': 0, 'Branch': 1, 'Jump': 0},
            'bgez': {'RegDst': 0, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 0,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 1, 'Jump': 0},
            'bgtz': {'RegDst': 0, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 0,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 1, 'Jump': 0},
            'blez': {'RegDst': 0, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 0,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 1, 'Jump': 0},
            'lb': {'RegDst': 0, 'ALUSrc': 1, 'MemToReg': 1, 'RegWrite': 1,
                   'MemRead': 1, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'lbu': {'RegDst': 0, 'ALUSrc': 1, 'MemToReg': 1, 'RegWrite': 1,
                    'MemRead': 1, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'lh': {'RegDst': 0, 'ALUSrc': 1, 'MemToReg': 1, 'RegWrite': 1,
                   'MemRead': 1, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'lhu': {'RegDst': 0, 'ALUSrc': 1, 'MemToReg': 1, 'RegWrite': 1,
                    'MemRead': 1, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'lw': {'RegDst': 0, 'ALUSrc': 1, 'MemToReg': 1, 'RegWrite': 1,
                   'MemRead': 1, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'lui': {'RegDst': 0, 'ALUSrc': 1, 'MemToReg': 0, 'RegWrite': 1,
                    'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'ori': {'RegDst': 0, 'ALUSrc': 1, 'MemToReg': 0, 'RegWrite': 1,
                    'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'sb': {'RegDst': 0, 'ALUSrc': 1, 'MemToReg': 0, 'RegWrite': 0,
                   'MemRead': 0, 'MemWrite': 1, 'Branch': 0, 'Jump': 0},
            'sh': {'RegDst': 0, 'ALUSrc': 1, 'MemToReg': 0, 'RegWrite': 0,
                   'MemRead': 0, 'MemWrite': 1, 'Branch': 0, 'Jump': 0},
            'slti': {'RegDst': 0, 'ALUSrc': 1, 'MemToReg': 0, 'RegWrite': 1,
                     'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'sltiu': {'RegDst': 0, 'ALUSrc': 1, 'MemToReg': 0, 'RegWrite': 1,
                      'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0},
            'sw': {'RegDst': 0, 'ALUSrc': 1, 'MemToReg': 0, 'RegWrite': 0,
                   'MemRead': 0, 'MemWrite': 1, 'Branch': 0, 'Jump': 0},

            # tipo J
            'j': {'RegDst': 0, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 0,
                  'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 1},
            'jal': {'RegDst': 0, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 1,
                    'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 1},
        }

        # Obtém o mnemonic em lowercase para garantir correspondência
        mnemonic = instr.mnemonic.strip().split()[0].lower()

        # Retorna os sinais de controle ou um padrão com zeros caso não encontrado
        return sinais_de_controle.get(mnemonic, {
            'RegDst': 0, 'ALUSrc': 0, 'MemToReg': 0, 'RegWrite': 0,
            'MemRead': 0, 'MemWrite': 0, 'Branch': 0, 'Jump': 0
        })

    @staticmethod
    def get_register_name(register_index: int) -> str:
        return MIPSDecoder.REGISTERS[register_index]

    @staticmethod
    def get_register_index(register_name: str) -> int:
        inv_map = { v: k for k, v in MIPSDecoder.REGISTERS.items() }
        return inv_map[register_name]


def parse_int(num_str: str) -> int:# aqui ele pega a instrução digitada, compreende qual base é e retorna ela convertida
    num_str = num_str.lower()
    base = 2 if num_str.startswith('0b') else 8 if num_str.startswith('0o') else \
           16 if num_str.startswith('0x') else 10
    return int(num_str, base)


def print_output(instr: Instruction, signals: dict) -> None:
    if instr.type == InstrType.R: #se for tipo R ele usa esse caminho pra imprimir o tipo da instrução no dict FUNCTIONS
        print(f'Instrução: {MIPSDecoder.FUNCTIONS.get(instr.fields.get("funct", 0), "Desconhecido")}')
    else:#Outros tipos ele consegue buscar direto o tipo da instrução pelo .name
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
        signals = decoder.get_sinais_de_controle(instr)
        print_output(instr, signals)


 ## para fins de testes descomente esse bloco, rode o código inserindo qquer instrução que ele passará por esse trecho testando vários outras instruções:
        # testes = [
        #     "00000000001000000000000000001000",  # jr $1              (funct=0x08)
        #     "00000000001000110001100000001001",  # jalr $3, $1        (funct=0x09)
        #     "00000000000000000001100000010000",  # mfhi $3            (funct=0x10)
        #     "00000000000000000001100000010010",  # mflo $3            (funct=0x12)
        #     "00000000001100000000000000010001",  # mthi $3            (funct=0x11)
        #     "00000000001100000000000000010011",  # mtlo $3            (funct=0x13)
        #     "00000000001100010000000000011000",  # mult $3, $1        (funct=0x18)
        #     "00000000001100010000000000011001",  # multu $3, $1       (funct=0x19)
        #     "00000000001100010000000000011010",  # div $3, $1         (funct=0x1A)
        #     "00000000001100010000000000011011",  # divu $3, $1        (funct=0x1B)
        #     "00000000000000100001100010000000",  # sll $3, $2, 4      (funct=0x00)
        #     "00000000000000100001100010000011",  # sra $3, $2, 4      (funct=0x03)
        #     "00000000000000100001100010000010",  # srl $3, $2, 4      (funct=0x02)
        #     "00000000001100100001100000000100",  # sllv $3, $2, $1    (funct=0x04)
        #     "00000000001100100001100000000110",  # srlv $3, $2, $1    (funct=0x06)
        #     "00000000001100100001100000000111",  # srav $3, $2, $1    (funct=0x07)
        #     "00000000000000000000000000001100",  # syscall            (funct=0x0C)
        #     "00000000000000000000000000001101",  # break              (funct=0x0D)
        #
        # # ==== Tipo I ====
        #     "00100000001000100000000000001010",  # addi $2, $1, 10
        #     "00100100001000100000000000001010",  # addiu $2, $1, 10
        #     "00110000001000100000000000001111",  # andi $2, $1, 15
        #     "00010000001000100000000000000100",  # beq $1, $2, 4
        #     "00000100001000010000000000001000",  # bgez $1, 8
        #     "00011100001000000000000000000100",  # bgtz $1, 4
        #     "00011000001000000000000000000100",  # blez $1, 4
        #     "00010100001000100000000000000100",  # bne $1, $2, 4
        #     "10000000001000100000000000010100",  # lb $2, 20($1)
        #     "10010000001000100000000000010100",  # lbu $2, 20($1)
        #     "10000100001000100000000000010100",  # lh $2, 20($1)
        #     "10010100001000100000000000010100",  # lhu $2, 20($1)
        #     "00111100000000100000000001100100",  # lui $2, 100
        #     "10001100001000100000000000010100",  # lw $2, 20($1)
        #     "11000100001000100000000000010100",  # lwc1 $2, 20($1)
        #     "00110100001000100000000000010101",  # ori $2, $1, 21
        #     "10100000001000100000000000010100",  # sb $2, 20($1)
        #     "00101000001000100000000000001100",  # slti $2, $1, 12
        #     "00101100001000100000000000001100",  # sltiu $2, $1, 12
        #     "10100100001000100000000000010100",  # sh $2, 20($1)
        #     "10101100001000100000000000010000",  # sw $2, 16($1)
        #     "11100100001000100000000000010100",  # swc1 $2, 20($1)
        #     "00111000001000100000000000011001",  # xori $2, $1, 25
        #
        #     # ==== Tipo J ====
        #     "00001000000000000000000000000100",  # j 4
        #     "00001100000000000000000000001000",  # jal 8
        # ]
        #
        # for bin_instr in testes:
        #     instr = MIPSDecoder().parse_instruction(bin_instr)
        #     signals = MIPSDecoder().get_sinais_de_controle(instr)
        #     print_output(instr, signals)


if __name__ == '__main__':
    main()

    #SE PRECISAR AQUI FICAM ALGUMAS INSTRUÇÕES PARA TESTAR O CÓDIGO MANUALMENTE:
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
