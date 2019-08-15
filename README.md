# LuaPytecode
Parses Lua 5.1 bytecode

# Example
```python
import luac

lc = luac.LuaCompiler()
chunk = lc.compileC("test.lua")

print("\n===== [[Disassembly]] =====\n")

def dis_chunk(chunk):
    print("==== [[" + str(chunk['NAME']) + "]] ====\n")
    for z in chunk['PROTOTYPES']:
        print("** decoding proto\n")
        dis_chunk(chunk['PROTOTYPES'][z])
    
    print("\n==== [[" + str(chunk['NAME']) + "'s constants]] ====\n")
    for z in chunk['CONSTANTS']:
        i = chunk['CONSTANTS'][z]
        print(str(z) + ": " + str(i['DATA']))

    print("\n==== [[" + str(chunk['NAME']) + "'s dissassembly]] ====\n")

    for z in chunk['INSTRUCTIONS']:
        i = chunk['INSTRUCTIONS'][z]
        if (i['TYPE'] == "ABC"):
            print(luac.lua_opcode_names[i['OPCODE']], i['A'], i['B'], i['C'])
        elif (i['TYPE'] == "ABx"):
            if (i['OPCODE'] == 1 or i['OPCODE'] == 5):
                print(luac.lua_opcode_names[i['OPCODE']], i['A'], -i['Bx']-1, chunk['CONSTANTS'][i['Bx']]['DATA'])
            else:
                print(luac.lua_opcode_names[i['OPCODE']], i['A'], -i['Bx']-1)
                
dis_chunk(chunk)
```

or just parse lua bytecode

```python
bytecode = "27\\76\\117\\97\\81\\0\\1\\4\\8\\4\\8\\0\\21\\0\\0\\0\\0\\0\\0\\0\\112\\114\\105\\110\\116\\40\\39\\104\\101\\108\\108\\111\\32\\119\\111\\114\\108\\100\\39\\41\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\2\\2\\4\\0\\0\\0\\5\\0\\0\\0\\65\\64\\0\\0\\28\\64\\0\\1\\30\\0\\128\\0\\2\\0\\0\\0\\4\\6\\0\\0\\0\\0\\0\\0\\0\\112\\114\\105\\110\\116\\0\\4\\12\\0\\0\\0\\0\\0\\0\\0\\104\\101\\108\\108\\111\\32\\119\\111\\114\\108\\100\\0\\0\\0\\0\\0\\4\\0\\0\\0\\1\\0\\0\\0\\1\\0\\0\\0\\1\\0\\0\\0\\1\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0".split('\\')
bytecode = list(map(int, bytecode))
lc = luac.LuaCompiler()
chunk = lc.decode_bytecode(bytecode)
```
