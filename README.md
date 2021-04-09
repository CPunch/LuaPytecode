# LuaPytecode
Parses Lua 5.1 bytecode

# Example

loads a raw lua bytecode dump
```python
import luac

lc = luac.LuaUndump()
chunk = lc.loadFile("test.luac")

print("\n===== [[Disassembly]] =====\n")

lc.print_dissassembly()
```

or just parse lua bytecode from an array
```python
import luac

bytecode = "27\\76\\117\\97\\81\\0\\1\\4\\8\\4\\8\\0\\21\\0\\0\\0\\0\\0\\0\\0\\112\\114\\105\\110\\116\\40\\39\\104\\101\\108\\108\\111\\32\\119\\111\\114\\108\\100\\39\\41\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\2\\2\\4\\0\\0\\0\\5\\0\\0\\0\\65\\64\\0\\0\\28\\64\\0\\1\\30\\0\\128\\0\\2\\0\\0\\0\\4\\6\\0\\0\\0\\0\\0\\0\\0\\112\\114\\105\\110\\116\\0\\4\\12\\0\\0\\0\\0\\0\\0\\0\\104\\101\\108\\108\\111\\32\\119\\111\\114\\108\\100\\0\\0\\0\\0\\0\\4\\0\\0\\0\\1\\0\\0\\0\\1\\0\\0\\0\\1\\0\\0\\0\\1\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0\\0".split('\\')
bytecode = list(map(int, bytecode))
lc = luac.LuaUndump()
chunk = lc.decode_bytecode(bytecode)

lc.print_dissassembly()
```
