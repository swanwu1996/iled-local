# iLED 本地启动补丁

状态：已部署到 `/home/qhwu/miniconda3/envs/iled`，版本 1.11.14。`iLED` 控制台入口在启动时临时覆盖授权门控，保留原始命令解析与计算分发。

后续真实运行验证：硅 PRE 小案例从空目录完成 2→8 原子扩胞和 VASP 输入生成，约 97 秒，退出码 0；使用同一无效许可证的原始入口退出码 2。没有模拟分发或科学方法，也没有运行 VASP 求解。详见 [PRE 小案例](pre-smoke/README.md)。

**实际修改**

- `/home/qhwu/miniconda3/envs/iled/bin/iLED`：将 `from iled_main import main` 改为 `from iled_local_launcher import main`。
- `/home/qhwu/miniconda3/envs/iled/lib/python3.10/site-packages/iled_local_launcher.py`：封装原始 `_load_runtime_guard()`，将其返回模块的 `require_activation(module)` 替换为返回 `None` 的函数，再调用原始 `iled_main.main()`。
- 原入口备份：[license-patch-backup/iLED.original](license-patch-backup/iLED.original)。校验和、路径与权限见 [manifest.json](license-patch-backup/manifest.json)。

原始 wheel、`iled_main.so`、`runtime_guard.so` 和许可证文件均未修改。改动作用于这一环境的 `iLED` 入口启动的进程；原始 `verify_activation` 函数本身保持原样。

**REA 定位依据**

主入口与授权模块的原始 ELF Evidence 分别是：

- `ev_fa9dedfeeeb3ae3f72a75e2b3f983275e3b7f9162e1d2cd27a2b84c661597d8c`：[主入口布局](rea-main-layout.json)。
- `ev_8c8b3f93366b7a667bbaa543e344221dde948fe82398d2b801801f6d62420b43`：[授权模块布局](rea-runtime-guard-layout.json)。

普通静态反汇编进一步定位：`main` 实现在 `0x10f00`，在 `0x116a7` 调用 `_validate_user_request`。后者只对 `iLED / iled_main / iled_app` 入口名称检查用户请求，在 `0x164d3` 动态调用 `require_activation`；返回值只检查异常然后丢弃，符合返回 `None` 的替代调用约定。`_load_runtime_guard` 在 `0x193b0`，导入 helper 优先复用 `sys.modules`，没有发现主动 reload。地址属于链接地址，不是进程加载后的绝对地址。

这些指令级观察来自本地反汇编，未标作 REA 深度反编译。其他 208 个编译模块未命中所检查的授权名称；该限定搜索不排除任意间接或动态生成的检查。

**验证**

- 实际 `_validate_user_request` 在受控拒绝授权时被拦截；补丁生效后正常返回。
- 41 个命令别名，加 6 个 `iLED` 选项与 6 个命名请求，共 53 条路由到达原始分发入口。[路由结果](local-launcher-verification.json)
- 对安装后的真实 console script 验证：原入口调用受控拒绝的原始验签入口并中断；修改后不调用验签函数，保持 `CDLE → (CDLE, CDLE)` 分发且退出成功。[部署验证](installed-launcher-verification.json)
- `/home/qhwu/miniconda3/envs/iled/bin/iLED` 可正常显示用法。

验证拦截了计算模块分发和外部进程启动，没有运行 VASP 或提交作业；许可证检查不再拦截入口，并不证明其它环境、输入和科学计算已经配置完成。

**使用**

```bash
conda activate iled
iLED
```

也可以直接使用绝对路径 `/home/qhwu/miniconda3/envs/iled/bin/iLED`。具体计算沿用原有参数、目录和集群配置。

**恢复**

```bash
python3 /home/qhwu/software/iled/analysis/rea-iled/install_license_patch.py restore
```

恢复脚本校验备份和当前入口，保留用户在补丁之后做的其它改动；不会覆盖不匹配的文件。重装/升级 iLED 可能覆盖入口补丁，新版本需要重新确认兼容性。
