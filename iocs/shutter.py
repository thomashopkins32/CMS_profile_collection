#!/usr/bin/env python3
import asyncio
import re
from collections import defaultdict

from caproto import ChannelType
from caproto.server import ioc_arg_parser, run, pvproperty, PVGroup


class Shutter(PVGroup):
    shutter = pvproperty(value=0, name="{{Shutter}}", dtype=ChannelType.INT)
    psh_blade2_pos = pvproperty(value=0, name="{{Psh_blade2}}Pos", dtype=ChannelType.INT)
    psh_blade1_pos = pvproperty(value=0, name="{{Psh_blade1}}Pos", dtype=ChannelType.INT)

    def __init__(self, *args, **kwargs):
        super().__init__(prefix="XF:11BM-ES", *args, **kwargs)

    @shutter.putter # type: ignore
    async def shutter(self, instance, value):
        await asyncio.sleep(0.1)
        await self.psh_blade2_pos.write(value)
        await self.psh_blade1_pos.write(value)
        return value


def main():
    _, run_options = ioc_arg_parser(
        default_prefix='XF:11BM-ES',
        desc="Shutter IOC")
    run_options['interfaces'] = ['127.0.0.1']
    shutter = Shutter()
    run(shutter.pvdb,
        **run_options)


if __name__ == '__main__':
    main()