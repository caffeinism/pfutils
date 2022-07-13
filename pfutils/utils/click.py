def global_option(ctx, param, value):
    if value is None:
        return ctx.obj[param.name] if param.name in ctx.obj else None
    else:
        ctx.obj[param.name] = value
        return value

def global_option_with_default(default):
    def _global_option(ctx, param, value):
        if value is None:
            if param.name not in ctx.obj:
                ctx.obj[param.name] = default

            return ctx.obj[param.name]
        else:
            ctx.obj[param.name] = value
            return value
    return _global_option