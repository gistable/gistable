import SCons.Defaults
import SCons.Builder

OriginalShared = SCons.Defaults.SharedObjectEmitter
OriginalStatic = SCons.Defaults.StaticObjectEmitter

def DoLint(env, source):
    for s in source:
        env.Lint(s.srcnode().path + ".lint", s)

def SharedObjectEmitter(target, source, env):
    DoLint(env, source)
    return OriginalShared(target, source, env)

def StaticObjectEmitter(target, source, env):
    DoLint(env, source)
    return OriginalStatic(target, source, env)

def generate(env):
    SCons.Defaults.SharedObjectEmitter = SharedObjectEmitter
    SCons.Defaults.StaticObjectEmitter = StaticObjectEmitter
    linter = SCons.Builder.Builder(
        action='$LINT $LINT_OPTIONS $SOURCE ; date > $TARGET',
        suffix='.lint',
        src_suffix='.c')
    env.Append(BUILDERS={'Lint': linter})

def exists(env):
    return 1