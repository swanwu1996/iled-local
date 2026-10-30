# iLED 1.11.14 编译模块静态调查

目标：`dist/iled-1.11.14-cp310-cp310-linux_x86_64.whl`。只提取和静态读取，没有 import、执行 CLI、提交作业或启动 VASP。未分析 `runtime_guard`，未检查或绕过许可逻辑。本文不是反编译源码，也不以文档字符串证明某次运行成功。

## 1. 制品与可恢复程度（已回答）

- Wheel 含 210 个 `.so`，安全提取总量 49,431,296 字节，完整成员名、SHA-256 和新绝对路径见 `extracted-so-index.json`。路径校验拒绝绝对路径和 `..`，未改原始 wheel。
- 排除 `runtime_guard` 后扫描 209 个模块，全部是 ELF64 x86-64 `DYN`，全部具有 Cython `__pyx_*`/`__Pyx_*` 符号，全部保留 `.symtab`，全部无 `.debug_info`。因此 **不是完全 stripped**，但没有 DWARF 源码行调试信息；可以恢复入口名、工作流标签和伪代码线索，不能称已恢复完整 Python 源码。
- `iled_main` 的 `_cython_3_1_8` 明确暴露 Cython 3.1.8 标记 [CM-S001]；模块文件和 wheel 标签为 CPython 3.10 Linux x86-64，导出 `PyInit_*` 并引用 CPython API。CPython ABI 结论主要来自包标签、成员后缀和符号，未用其它 Python 版本实际加载验证。
- 每个扫描模块 `DT_NEEDED` 仅有 `libpthread.so.0` 和 `libc.so.6`；这不等于 Python 运行时只依赖这两项，Python-level imports 及外部计算程序是独立依赖。全部带同一构建环境 RPATH `/public/home/huangmenglin/envs/migrate-all/lib`。该绝对路径是构建痕迹，是否在用户机器上影响加载尚未运行验证。
- 方法和逐模块计数：`compiled-module-metadata.json`，原始地址化符号：`compiled-symbols.jsonl`，原始偏移化 UTF-8 常量：`compiled-strings.jsonl`。字符串索引有无效 UTF-8/小于4字节/大于20000字节筛选边界，符号索引为 `nm --defined-only`。

## 2. 总入口和分发（已回答入口，未建立完整指令级调用图）

`iled_main.main` 的 Python包装入口 [CM-F002] 和主体局部符号 [CM-F003] 保留。`_dispatch` 存在，其文档写明导入模块后执行 `mod.main()`，并隔离 `sys.path` [CM-S004]；`_base_dir` 返回包含 CDLE/TSLE/ESLE 的目录 [CM-S005]。

内嵌帮助直接列出主选项：`iLED -pre / -tsle / -cdle / -adle / -nsle / -esle`，分别称为预处理、热力学稳定性、缺陷能级、主动数据学习、非辐射捕获/瞬态、载流子浓度 [CM-S006][CM-S007][CM-S008]。帮助还说兼容 `-1`、`-2`、`-3`、`-4` [CM-S009]。

内嵌说明宣称 PyInstaller 单可执行文件可以由符号链接 `argv[0]` 分发 [CM-S010]; **这是实现意图文本，不能证明本次 wheel 已经过 PyInstaller 打包**。

可直接观察的分发字符串包括 `PRE/PRE_static/PRE_final/PRE_aexx/PRE_aexx_fin`、`CDLE/CDLE_neu_relax/CDLE_neu_static/CDLE_chg_relax/CDLE_chg_static/CDLE_correction/CDLE_plot`、`CDLE_mlip/ CDLE_mlip_stage1..5`、`TSLE_relax/TSLE_static/TSLE_analysis/TSLE_analysis2/TSLE_cycle`、`ADLE_stage1..5`、`NSLE_1D_cli/NSLE_MD_cli/NSLE_PL_cli/NSLE_transient_run`、`MLCD_workflow/MLCD_stage_runner/MLCD_callback`、`ESLE_calcu`。这些是常量表观察；仅凭名称不能证明每个分支都可达。

新 CDLE 运行存在 `_reset_cdle_runtime_state` [CM-F011]，文档说明清理 transient CDLE/MLCD 状态 [CM-S012]；字符串显示 `.iled_state`、`.q*_relax_tmp`、`.q*_static_tmp`、`q*_relax_proc.log`、`q*_static_proc.log`、`*.pending`、`.*.lock` 等候选清理模式。未执行清理。

## 3. 科学工作流（静态文档/名称证明存在，数值正确性未验证）

### PRE / CDLE

CDLE 主入口和 `CDLEWorkFlow` 局部方法符号完整保留；包括中性/带电的 relax/static 作业及日志管理。`CDLE.CDLE` 文本直接宣称创建 host POSCAR、intrinsic、dopant 和隐藏日志目录 [CM-S013][CM-S014][CM-S015]。可见输入 `iLED.para` 和输出 `cdle.json`；`POSCAR_unrelaxed/POSCAR_primitive/POSCAR_relaxed` 为结构文件角色线索。

CDLE 的 IAI 后端选择有 `_normalize_iai_backend/_read_iai_backend/_run_cdle_mlip` 局部函数；主流程可选择 MLIP 路线是合理推断，但尚未解开完整参数到分支映射。`CDLE_mlip` 内嵌提示：未配置 scheduler cluster 时只准备提交脚本 [CM-S016]。

电荷修正文档/错误文本覆盖 FNV、SLABCC、FNV2D；二维缺陷参数明确写 `CDLE_2D=T` 且限制3D修正，建议 `SLABCC` 或 `FNV2D` [CM-S017]。`correction_import.fnv_correction` 函数存在，错误文本要求 `sxdefectalign` [CM-S018]。这证明依赖名称和分支意图，没有验证修正值。

### TSLE

主入口帮助称热力学稳定性。`TSLE.tsle` 文本指示读 competing phases、准备 POSCAR、`relax1 -> relax2`，然后 analysis/re-static/re-analysis；POTCAR版本不匹配时 `Scheme 0` 明确说跳过 DFT，仅做定性分析 [CM-S019][CM-S020]。

`TSLE.analysis` 错误/结果文本含 `e_hull` 与 thermodynamically unstable，支持 convex-hull 稳定性分析判断 [CM-S021]；re-static 特殊处理 O2 triplet `NUPDOWN=2` 和气相 `NCORE=1` 的文档直接保留 [CM-S022][CM-S023]。`analysis2` 文本指向 refined DFT energies 的再分析 [CM-S024]。

### ADLE

`ADLE.adle.prepare/submit/main` 三入口均保留；提交前准备 ADLE输入及 scheduler script，配置/状态含 `adle.json`。`ADLE.calcu` 具有丰富可恢复局部函数：缺陷结构库生成、DFT轨迹提取、extxyz导出、NequIP/Allegro YAML生成、模型训练/部署/评估、ASE松弛、按电荷交叉验证、最终DFT替换、缺陷形成能/跃迁能级/图表。

五阶段的**内嵌文档**明确写：

1. 准备 VASP 输入并提交 VASP阶段 [CM-S025]。
2. 检查 VASP，构建训练数据并按需提交训练 [CM-S026]。
3. 检查/部署模型，评估，松弛结构并分析 [CM-S027]。
4. 分析 MLIP 推断并可提交 final_dft 替换 [CM-S028]。
5. final_dft 完成后收尾混合 DFT/MLIP 结果 [CM-S029]。

能力边界十分具体：MACE/SevenNet 支持目前是 placeholder，要求用户按已测CLI配置 `train_command/deploy_command/checkpoint_file/model_file` [CM-S030]。因此不能把 ADLE 宣称为这些框架全部开箱即用。NequIP CLI字符串 `nequip-train/nequip-compile` 和 `NequIPCalculator` 是可见的集成线索。

### ESLE

`ESLE.calcu` 文档写明读取 `esle.json` 并从稳定电荷态/跃迁重建形成能 [CM-S031]；分别求生长温度平衡和工作温度、冻结缺陷总量后重新分配电荷态 [CM-S032]。Fermi level采用二分法的文档、`_solve_fermi/_solve_fermi_frozen` 符号保留 [CM-S033]。

输出文档含 EF/n0/p0/缺陷浓度的四联图、化学势路径CSV、物理参数JSON；路径文本 `esle/esle_metadata.json` [CM-S034][CM-S035]。二分法的收敛说明属于作者内嵌文档；未数值验证退化区间等边界。

### NSLE分支 / 1D / multi-D / PL / transient

`NSLE.nsle` 明确要求 `iLED.para` 中 `NSLE_job` [CM-S036]，有效候选提示 `nonrad-1d, nonrad-md, pl-md, or transient` [CM-S037]; `_run_1d/_run_multid/_run_pl_md/_run_transient` 均有入口符号。PL分支尚不支持 `NSLE_force/NSLE_dry_run` 的错误文本直接存在 [CM-S038]。

1D pipeline 的阶段名称构成 PES准备/路由/提交/检查 -> PES拟合 -> Wif AE或Wif DFT -> lineshape -> Sommerfeld -> capture；生成Slurm控制脚本并保留 `.iled_pipeline_*`、`state.json/jobs.json`、`capture_coefficient.json/png` [CM-S039][CM-S040][CM-S041]。`nsle1d.capture` 文档直接写最终系数为 Sommerfeld修正且单位cm³/s [CM-S042]。

multi-D pipeline 常量包含训练结构生成、training DFT、XYZ收集、SevenNet训练、Gamma phonon或phonopy-DFT路径、cartesian AE Wif、Wif模式投影和 capture；这些步骤的默认启用条件尚未指令级恢复。`nslemd.capture` 文档非常具体：equal-mode可取 `J=I`，仍保留 full mode-mode matrix 的非对角项；完整 Duschinsky 可选初态基/末态基 [CM-S043][CM-S044]。最终表达式字符串为 `|sum_kl L_kl W_k W_l| * V * atomic_time^-1 * degeneracy * Sommerfeld` [CM-S045]。不能把该包概括为只有1D模型或只有模式对角求和。

transient 有 material/kinetic model 构建、电子/空穴发射、各电荷态占据、generation G(t)、equilibrium guess 和动力学solver函数。文档直接说先做 G=0平衡，再积分请求的 G(t)，且在 G(t)节点拆分积分 [CM-S046][CM-S047]；正向载流子质量作用约束 `n*p >= ni²` 及 stiff integration 的 direct steady fallback 文本保留 [CM-S048][CM-S049]。输出候选为 `equilibrium.csv/transient.csv/channel_rates.csv/net_capture_rates.csv/summary.json/result.json`。

### MLCD

MLCD compatibility entrypoint 文档为 defect CHGCAR workflow library [CM-S050]。CLI帮助写明全训练流程 `relax -> static -> collect CHGCAR -> EAC train` [CM-S051]；可准备中性/带电结构、CHGCAR->h5、EAC训练/预测、缺陷嵌入、PAW augmentation graft、NSCF和EAC+VASP NSCF力驱动ASE BFGS松弛 [CM-S052][CM-S053]。输出目录常量包括 `relax/neutral/defect/n_*/...`、`charged/q_*/defect/n_*/...`、`supercells/defect/n_*` 和 JSON manifests。CLI提供 `--no-submit/--no-wait/--vasp-command/--eac-bin/--charge/--embedding-manifest/--config` 等参数。

## 4. 外部依赖与可能的运行环境（部分回答）

- 直接ELF依赖只有 libc/libpthread；Python-level imports不能从DT_NEEDED推断。
- Slurm `sbatch` / 提交脚本，VASP、`sxdefectalign`，EAC训练/预测CLI，ASE、pymatgen/vasp_io、NequIP/Allegro、phonopy、SevenNet等名称可见于函数、错误/帮助文本或脚本常量。它们的安装状态、版本兼容性和执行授权均未验证。
- **推断**：iLED整体更像围绕缺陷DFT及机器学习替代的科学工作流编排器，串接结构/任务准备、调度、收敛检查、数据收集、数值分析和可视化；不是单一数值求解内核。此推断由上述入口、阶段、调度和输出证据共同支持。
- 科学正确性、作业资源设置是否适合本机、默认文件覆盖行为、所有参数缺省值和误差阈值仍未知。没有执行目标，因此没有成功完成某个科学任务的证据。

## 5. 证据索引

下列 CM-ID 是本调查生成的本地静态证据ID，**不是 REA MCP Evidence IDs**。机器可读对应为 `compiled-curated-evidence.json`；全量低级索引可按成员名+offset/symbol重用。

- CM-S001: `iled_main.cpython-310-x86_64-linux-gnu.so` @ file offset `0x1a0f3` — `_cython_3_1_8`
- CM-F002: `iled_main.cpython-310-x86_64-linux-gnu.so` symbol `__pyx_pw_9iled_main_15main` @ ELF virtual address `0x0000000000015870`
- CM-F003: `iled_main.cpython-310-x86_64-linux-gnu.so` symbol `__pyx_pf_9iled_main_14main.isra.50` @ ELF virtual address `0x0000000000010f00`
- CM-S004: `iled_main.cpython-310-x86_64-linux-gnu.so` @ file offset `0x1aa40` — `Import and run mod.main() with proper sys.path isolation.`
- CM-S005: `iled_main.cpython-310-x86_64-linux-gnu.so` @ file offset `0x1aaa0` — `Return the base directory that contains CDLE/, TSLE/, ESLE/.`
- CM-S006: `iled_main.cpython-310-x86_64-linux-gnu.so` @ file offset `0x1ab40` — `Usage: iLED <-pre|-tsle|-cdle|-adle|-nsle|-esle>`
- CM-S007: `iled_main.cpython-310-x86_64-linux-gnu.so` @ file offset `0x1ac52` — `    iLED -adle       Run ADLE (active data learning)`
- CM-S008: `iled_main.cpython-310-x86_64-linux-gnu.so` @ file offset `0x1ac87` — `    iLED -nsle       Run NSLE (nonradiative capture / transient)`
- CM-S009: `iled_main.cpython-310-x86_64-linux-gnu.so` @ file offset `0x1ae80` — `Legacy flags are still accepted: -1, -2, -3, -4.`
- CM-S010: `iled_main.cpython-310-x86_64-linux-gnu.so` @ file offset `0x1ad7a` — `the dispatch table routes to the correct module based on argv[0].`
- CM-F011: `iled_main.cpython-310-x86_64-linux-gnu.so` symbol `__pyx_pw_9iled_main_1_reset_cdle_runtime_state` @ ELF virtual address `0x0000000000019100`
- CM-S012: `iled_main.cpython-310-x86_64-linux-gnu.so` @ file offset `0x1aae0` — `Clear transient CDLE/MLCD state when the user starts a new CDLE run.`
- CM-S013: `CDLE/CDLE.cpython-310-x86_64-linux-gnu.so` @ file offset `0x2a5e0` — `CDLE module initializing, create host POSCAR directory: `
- CM-S014: `CDLE/CDLE.cpython-310-x86_64-linux-gnu.so` @ file offset `0x2a580` — `CDLE module initializing, create intrinsic calculation directory: `
- CM-S015: `CDLE/CDLE.cpython-310-x86_64-linux-gnu.so` @ file offset `0x2a540` — `CDLE module initializing, create dopant calculation directory: `
- CM-S016: `CDLE_mlip/cdle_mlip.cpython-310-x86_64-linux-gnu.so` @ file offset `0xc980` — `No scheduler cluster was configured; CDLE_mlip submit script was prepared only.`
- CM-S017: `CDLE/CDLE_correction.cpython-310-x86_64-linux-gnu.so` @ file offset `0x51fc0` — `CDLE_2D=T does not use 3D charge correction '%s'; using None. Use CDLE_charge_correction=SLABCC or FNV2D for charged 2D defects.`
- CM-S018: `CDLE/correction_import.cpython-310-x86_64-linux-gnu.so` @ file offset `0x13ba0` — `. Check that sxdefectalign exists at `
- CM-S019: `TSLE/TSLE/tsle.cpython-310-x86_64-linux-gnu.so` @ file offset `0x11800` — `Scheme 0 selected (POTCAR version mismatch): skipping DFT, running qualitative analysis only.`
- CM-S020: `TSLE/TSLE/tsle.cpython-310-x86_64-linux-gnu.so` @ file offset `0x117c0` — `relax1 already converged, submitting relax2...`
- CM-S021: `TSLE/TSLE/analysis.cpython-310-x86_64-linux-gnu.so` @ file offset `0x4cdc0` — `Compound is thermodynamically unstable (e_hull = `
- CM-S022: `TSLE/TSLE/analysis.cpython-310-x86_64-linux-gnu.so` @ file offset `0x4cc60` — `Use triplet O2 (S=1, NUPDOWN=2) for gas-phase O2 re-static jobs.`
- CM-S023: `TSLE/TSLE/analysis.cpython-310-x86_64-linux-gnu.so` @ file offset `0x4cbc0` — `Use NCORE=1 for tiny gas-phase re-static jobs.`
- CM-S024: `TSLE/TSLE/analysis2.cpython-310-x86_64-linux-gnu.so` @ file offset `0x41a40` — `Starting re-analysis with refined DFT energies (`
- CM-S025: `ADLE/calcu.cpython-310-x86_64-linux-gnu.so` @ file offset `0x329200` — `Stage 1: prepare VASP inputs and always submit the VASP-stage script.`
- CM-S026: `ADLE/calcu.cpython-310-x86_64-linux-gnu.so` @ file offset `0x3291a0` — `Stage 2: verify VASP, build training data, and submit training when needed.`
- CM-S027: `ADLE/calcu.cpython-310-x86_64-linux-gnu.so` @ file offset `0x329140` — `Stage 3: check/deploy model, evaluate, relax structures, and analyze outputs.`
- CM-S028: `ADLE/calcu.cpython-310-x86_64-linux-gnu.so` @ file offset `0x3290e0` — `Stage 4: analyze MLIP inference and optionally submit final_dft replacements.`
- CM-S029: `ADLE/calcu.cpython-310-x86_64-linux-gnu.so` @ file offset `0x329080` — `Stage 5: finalize mixed DFT/MLIP results after final_dft has finished.`
- CM-S030: `ADLE/calcu.cpython-310-x86_64-linux-gnu.so` @ file offset `0x332040` — `MACE/SevenNet support is currently a placeholder in ADLE. Set train_command, deploy_command/checkpoint_file/model_file according to the tested framework CLI.`
- CM-S031: `ESLE/ESLE/calcu.cpython-310-x86_64-linux-gnu.so` @ file offset `0x76ae0` — `Read esle.json and reconstruct stable charge-state formation energies.`
- CM-S032: `ESLE/ESLE/calcu.cpython-310-x86_64-linux-gnu.so` @ file offset `0x76ee8` — `    Total concentration of each defect is frozen from growth-temperature`
- CM-S033: `ESLE/ESLE/calcu.cpython-310-x86_64-linux-gnu.so` @ file offset `0x77000` — `Vectorised bisection solver for the charge-neutrality Fermi level.`
- CM-S034: `ESLE/ESLE/calcu.cpython-310-x86_64-linux-gnu.so` @ file offset `0x76d40` — `Draw the 4-panel figure (EF / n0 / p0 / defect concentrations) and save.`
- CM-S035: `ESLE/ESLE/calcu.cpython-310-x86_64-linux-gnu.so` @ file offset `0x77420` — `Wrote esle/esle_metadata.json — snapshot of physical parameters (T₁, T₂, Eg, m_e*, m_h*, hull endpoints) for reproducibility.`
- CM-S036: `NSLE/nsle.cpython-310-x86_64-linux-gnu.so` @ file offset `0x12b00` — `NSLE requires NSLE_job in iLED.para`
- CM-S037: `NSLE/nsle.cpython-310-x86_64-linux-gnu.so` @ file offset `0x12b40` — `; use nonrad-1d, nonrad-md, pl-md, or transient`
- CM-S038: `NSLE/nsle.cpython-310-x86_64-linux-gnu.so` @ file offset `0x12b80` — `NSLE_job = pl-md does not support NSLE_force or NSLE_dry_run yet`
- CM-S039: `nsle1d/pipeline.cpython-310-x86_64-linux-gnu.so` @ file offset `0x34280` — `Generate Slurm stage scripts for the full workflow.`
- CM-S040: `nsle1d/pipeline.cpython-310-x86_64-linux-gnu.so` @ file offset `0x34ea0` — `stage_03_fit_pes`
- CM-S041: `nsle1d/pipeline.cpython-310-x86_64-linux-gnu.so` @ file offset `0x34e80` — `stage_07_capture`
- CM-S042: `nsle1d/capture.cpython-310-x86_64-linux-gnu.so` @ file offset `0x19ea0` — `Compute the Sommerfeld-corrected capture coefficient in cm^3/s.`
- CM-S043: `nslemd/capture.cpython-310-x86_64-linux-gnu.so` @ file offset `0xb0899` — `    Duschinsky expression. The off-diagonal part is retained through the`
- CM-S044: `nslemd/capture.cpython-310-x86_64-linux-gnu.so` @ file offset `0xb0e40` — `Dispatch the non-EMA calculation to the selected Duschinsky basis.`
- CM-S045: `nslemd/capture.cpython-310-x86_64-linux-gnu.so` @ file offset `0xb2240` — `C_all = |sum_kl L_kl W_k W_l| * V * atomic_time^-1 * degeneracy * Sommerfeld`
- CM-S046: `nsle_transient/solver.cpython-310-x86_64-linux-gnu.so` @ file offset `0x67160` — `Run G=0 equilibrium pre-run, then transient with the requested G(t).`
- CM-S047: `nsle_transient/solver.cpython-310-x86_64-linux-gnu.so` @ file offset `0x66f40` — `Integrate transient equations, forcing solver boundaries at G(t) knots.`
- CM-S048: `nsle_transient/solver.cpython-310-x86_64-linux-gnu.so` @ file offset `0x66e80` — `Return values with nonnegative carriers constrained to n*p >= ni^2.`
- CM-S049: `nsle_transient/solver.cpython-310-x86_64-linux-gnu.so` @ file offset `0x67040` — `Solve the G=0 steady state directly if time integration is too stiff.`
- CM-S050: `MLCD/auto_defect_chgcar_workflow.cpython-310-x86_64-linux-gnu.so` @ file offset `0x4360` — `Compatibility entrypoint for the defect CHGCAR workflow project library.`
- CM-S051: `MLCD/defect_chgcar_workflow/cli.cpython-310-x86_64-linux-gnu.so` @ file offset `0x37aa0` — `Full training workflow: relax -> static -> collect CHGCAR -> EAC train`
- CM-S052: `MLCD/defect_chgcar_workflow/cli.cpython-310-x86_64-linux-gnu.so` @ file offset `0x38100` — `Prepare an ASE BFGS loop driven by EAC rho prediction and VASP NSCF forces`
- CM-S053: `MLCD/defect_chgcar_workflow/cli.cpython-310-x86_64-linux-gnu.so` @ file offset `0x382e0` — `Graft PAW augmentation into EAC-predicted CHGCAR and prepare NSCF folders`
