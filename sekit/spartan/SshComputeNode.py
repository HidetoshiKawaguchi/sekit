# -*- coding: utf-8 -*-
from subprocess import Popen, getoutput
from typing import Any, Sequence, cast

from .ComputeNode import ComputeNode, ComputeNodeThread


class SshComputeNodeThread(ComputeNodeThread):
    def exe_command(self) -> Popen[Any]:
        ssh_header = "ssh " + self.p_cn.hostname + " "
        out_cmd = ""
        for c in cast(str, self.cmd).strip(" ;").split(";"):
            one_cmd = ssh_header + "'{} ; {};'".format(
                cast(Any, self.p_cn).pre_cmd, c
            )
            out_cmd += one_cmd + " ; "
        return cast("Popen[Any]", Popen(out_cmd, shell=True))


class SshComputeNode(ComputeNode):
    def __init__(
        self,
        hostname: str,
        n_jobs: int = 1,
        interval: int | float = 1,
        thread_name: str | None = None,
        device: Sequence[str] | None = None,
        device_key: str = "_device",
        pre_cmd: str = "source .bash_profile",  # TODO: 何かいい書き方はないものか
    ) -> None:
        super().__init__(
            n_jobs=n_jobs,
            interval=interval,
            device=device,
            device_key=device_key,
            thread_name=cast(str, thread_name),
        )
        self.pre_cmd = pre_cmd
        self.hostname = hostname
        if thread_name is None:
            thread_name = hostname

        if n_jobs < 0:
            cmd_grep_processor = (
                "ssh "
                + self.hostname
                + ' "grep processor /proc/cpuinfo" | '
                + "wc -l"
            )
            n_jobs = int(getoutput(cmd_grep_processor))
            self.n_jobs = n_jobs
        else:
            self.n_jobs = n_jobs

    def _start_thread(self, index: int | str) -> None:
        thread_name = "{}_{}".format(self.thread_name, index)
        thread = SshComputeNodeThread(p_cn=self, name=thread_name)
        thread.start()
        self.threads.append(thread)
