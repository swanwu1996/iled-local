# iLED 1.11.14：打包接口与可见工作流

分析对象：`dist/iled-1.11.14-cp310-cp310-linux_x86_64.whl`。只使用 Python 标准库 `zipfile` 读取成员，未导入任何 iLED 模块、未执行其脚本、未提交计算。下文 `成员:行号` 指 wheel 内文本成员原始行号。本文补充主调查的 REA 归档证据；这些文本读取本身没有 REA Evidence ID。

小型文本成员已按原始目录安全复制到 `analysis/rea-iled/interface-files`，没有改写源码。关键可点击来源：[METADATA](/home/qhwu/software/iled/analysis/rea-iled/interface-files/iled-1.11.14.dist-info/METADATA:2)、[42个console_scripts](/home/qhwu/software/iled/analysis/rea-iled/interface-files/iled-1.11.14.dist-info/entry_points.txt:1)、[PL入口](/home/qhwu/software/iled/analysis/rea-iled/interface-files/nsle_pl_runtime/pl.sh:273)、[非嵌入流程](/home/qhwu/software/iled/analysis/rea-iled/interface-files/nsle_pl_runtime/pl_without_embedding.sh:468)、[嵌入流程](/home/qhwu/software/iled/analysis/rea-iled/interface-files/nsle_pl_runtime/pl_embedding.sh:1090)、[ICCP导出](/home/qhwu/software/iled/analysis/rea-iled/interface-files/cor_byy/iccp/__init__.py:1)。

## 已直接观察的身份与接口

- 名称 iLED、版本 1.11.14；描述为 “Integrated workflow for electronic-level defect calculations”，许可证 Proprietary。不是照明/显示控制程序。证据：`iled-1.11.14.dist-info/METADATA:2–6`。
- 构建标签为 `cp310-cp310-linux_x86_64`，`Root-Is-Purelib: false`。虽然 METADATA 写 Python >=3.10，这一具体 wheel 绑定 CPython 3.10/Linux x86-64。证据：`WHEEL:3–4` 与 `.cpython-310-x86_64-linux-gnu.so` 成员名。
- 声明依赖 ASE、cryptography、dpdata、h5py、matplotlib、mp-api、numpy、pandas、phonopy、pymatgen、PyYAML、requests、scipy、spglib。证据：`METADATA:7–20`。这些是依赖声明，不证明每个分支都调用它们。
- **42 个控制台命令全部映射到 `iled_main:main`**：iLED；ADLE 及 stage1–5；CDLE 及中性/带电 relax/static/correction/plot；CDLE_mlip 及 stage1–5；PRE/aexx/aexx_fin/final/static；TSLE/analysis/analysis2/cycle/relax/static；ESLE/calcu；MLCD_workflow/callback/stage_runner；NSLE/1D/MD/PL/transient；ICCP_bundled。证据：`entry_points.txt:2–43`。
- 推断：统一入口可能根据命令名分派；entry_points 自身**不证明** `sys.argv[0]` 分派、具体函数映射或许可检查顺序，需主调查的编译入口证据补足。

## 功能边界

| 模块 | 直接可见材料 | 结论与边界 |
|---|---|---|
| CDLE | `CDLE_chg_relax`、`CDLE_chg_static`、`CDLE_neu_relax`、`CDLE_neu_static`、`CDLE_correction` 控制台名；`CDLE/sxdefectalign` | 存在带电/中性缺陷计算与修正接口；完整阶段条件仍在编译模块中。 |
| CDLE_mlip | `CDLE_mlip/__init__.py:1` 明确 “defect-targeted MLIP datasets” | 缺陷定向机器学习势数据集模块；5 个 stage 的意义无法仅由文件名恢复。 |
| MLCD | `MLCD/defect_chgcar_workflow/__init__.py:1` 明确 defect/bulk CHGCAR dataset preparation | 缺陷/体相 CHGCAR 数据集准备。`__init__.py:10–27` 还会在导入时配置可写 matplotlib 缓存，本次没有执行。 |
| ICCP | `cor_byy/__init__.py:1` 明确 charged-defect correction；`cor_byy/iccp/__init__.py:1–35` 导出 run_sz/run_fnv/run_fnv2d/run_slabcc/run_pa/run_lz/run_zwd/run_madelung、prepare/parse_scpc、detect_charge/interfaces/position 等 | 多方法带电缺陷修正接口，含 2D/slab 路径。具体公式/适用性未验证。 |
| NSLE 1D | `nsle1d/__init__.py:1–11` 明确 1D nonradiative-capture，导出 mass_weighted_delta_q | 一维非辐射俘获工作流；封装存在 prepare/submit PES、fit_pes、prepare_wif_dft、capture/lineshape/sommerfeld 的编译 CLI，但顺序只是待验证候选。 |
| NSLE MD | `nslemd/__init__.py:1–25` 明确 multi-D nonradiative-capture，导出 PhononBackend/PhononPlan/MlipSettings/EMA/Sommerfeld | 多维非辐射俘获与声子/MLIP接口；训练、声子、WIF阶段内部控制仍编译。 |
| NSLE transient | `nsle_transient/__init__.py:1` 明确 transient NSLE rate-equation solver | 瞬态速率方程模块。 |
| NSLE PL | `nsle_pl_runtime/pl.sh:267` 明确 PL spectrum calculation；3 个完整 shell 成员 | 可直接读出光致发光谱、声子、嵌入/非嵌入流程，见下文。 |
| ADLE | `ADLE/allegro.yaml:22–27,39–46,71–75,96–98`；`ADLE/lxp/submit_allegro:16`；`submit_lmp:21–22` | Allegro 能量/力训练模板与 LAMMPS 执行脚本；不能据此解释 ADLE 缩写或保证当前主路径使用旧 lxp 示例。 |
| TSLE / ESLE | submit.yaml 中 VASP/PBS/Slurm 模板；TSLE mpdata.csv/POSCAR.zip | 有独立 VASP 流程及大规模材料结构/能量资源；精确物理任务待编译模块证据。 |

## 可直接恢复的 NSLE PL 流程

`nsle_pl_runtime/pl.sh`：

1. 选用户工作目录，读取 `iLED.para`，记录到 `iLED.log`（14–25,35–48）；导出队列、节点、核数、VASP路径、POTCAR路径、温度、EMA、位移幅度、嵌入与谱展宽参数（168–210）。只在 `NSLE_job=pl-md` 时继续（261–265）。
2. 工作目录为 `nsle/pl-md_${defect}_${initial_charge}_to_${final_charge}`（233–252）。准备 bulk/initial/final/PL，体相输入来自根目录 POSCAR，并按元素拼接 POTCAR（132–155,273–281）。
3. 若 `NSLE_from_CDLE` 为真，则从 `cdle.json` 的 `defect[名称].charge/intercept` 计算电荷转变能级；按电荷方向选择 `Eg-transition_level` 或 `transition_level`，带隙外退出（80–120,283–300）。查找 `cdle/.../缺陷/q电荷/static` 作为初末态来源；否则读取手工初末态目录与 deltaE（299–312）。
4. 生成单进程包装 Slurm 作业并 `sbatch --parsable` 提交子脚本；按 `NSLE_embedding` 选择 embedding 或 without_embedding（315–355,379–388）。这里**没有阻塞等待**：原注释声称等待，但 squeue/sacct 循环已注释（359–376）。

**非嵌入分支** `pl_without_embedding.sh`：

- 初末态 CONTCAR → `CONTCAR_ES.vasp/CONTCAR_GS.vasp`；按 EMA 选一态生成声子位移（468–499）。
- `phonopy-init -d --dim 1 1 1` → 每个 POSCAR 位移的 VASP SCF目录；INCAR 设置 NSW=0、IBRION=2、ISIF=2、EDIFF默认 1E-07（499–518）。
- 将 SCF 用 Slurm 数组分批提交，并以 `%max_job` 限制并行；squeue 轮询各批（243–328,519–548）。
- 收集 `vasprun.xml`，运行 `phonopy-init -f`、提交 `phonopy --writefc --full-fc`，生成含 Γ 点本征矢的 band.yaml（551–579）。
- 最终提交 `NSLE_PL_cli pl_without_embedding`，传递初末态结构、band.yaml、ZPL能量、温度、分辨率与谱展宽，再轮询 Slurm（333–384,586–638）；主函数先声子后 PL（641–664）。

**嵌入分支** `pl_embedding.sh`：

- 顺序是 host → defect → supercell → PL（1136–1207）。host 通过 LU_scanning 扩胞，默认约300–400原子，再声子/力常数（632–668）。
- 若需要扩大缺陷胞，生成嵌入 GS/ES结构并提交弛豫；按原始中性电子数与 INCAR NELECT计算电荷，再映射到新的中性电子数，维持初末态电荷（865–936）。
- EMA选择缺陷初态/末态声子，并沿用相应 NELECT（948–995）。
- 将缺陷嵌入约1000至 PL_MAX_ATOMS（默认2500）原子的超胞，并生成 marker（1070–1086）。
- 最后将 host/defect FORCE_CONSTANTS、GS/ES 超胞、marker 与谱参数传给 PL计算，结束后调用 plot_with_outputdata（1160–1217）。矩阵拼接/谱积分的内部算法在 `.so`，本文没有验证。

## 调度模板与数据资源

- `ESLE/ESLE/submit.yaml:16–32` 与 `TSLE/TSLE/submit.yaml:18–36` 同时携带 PBS 和 Slurm 模板，Slurm 通过 `mpirun -n total_cores vasp_std` 运行；TSLE另有 walltime 参数。`ADLE/submit.yaml`、`CDLE_mlip/submit.yaml` 的 Slurm 部分只有资源头部，不能将其解读为完整可独立运行脚本。
- Allegro模板包含 Ga/N 示例、extxyz训练路径、36训练/7验证数据、能量/力损失、float64和Adam（`ADLE/allegro.yaml:22–27,39–46,68,96–98,119–125`）。lxp脚本中CUDA/LAMMPS绝对路径、partition/module命令是特定集群示例配置，并不适用于任意主机。
- `TSLE/TSLE/mpdata.csv` 有155094条数据行，首行字段为 `mpid,uncorrected_energy_per_atom,ehull_per_atom,chemsys`。嵌套 `POSCAR.zip` 共326861个ZIP成员，其中326860个非目录成员。两者的规模/计数为直接观察，配对关系、数据库版本及数据授权来源未知。

## 静态可见的风险与缺口

1. **完成判定偏弱**：两分支的SCF数组只检查 OUTCAR是否存在即跳过（`pl_without_embedding.sh:319–322`; `pl_embedding.sh:545–548`）；vasprun_ready/wait只按文件存在计数，未解析收敛/完整性（前者389–462；后者557–629）。Slurm消失后报告完成，未在这些可见路径强制验证COMPLETED。失败、截断结果可能被当作完成，这是静态推断，未执行验证。
2. **非嵌入计数可能受 `set -e` 影响**：脚本2行打开errexit，`wait_for_all_vasprun` 的425行和435行有裸 `((expected++))`/`((count++))`，初值为0时算术命令退出状态为1；该函数在555行作为独立命令调用，可能首轮退出。`all_vasprun_ready`在if条件内调用，不能笼统宣称所有同类计数都会触发退出；嵌入函数的计数也需结合完整调用上下文分析。这是Bash语义推断，未运行目标脚本。
3. **fallback不完整**：`pl_embedding.sh:14–19` 与 `pl_without_embedding.sh:14–19` 在找不到 NSLE_PL_cli 时调用同目录 pl_cli.py；wheel只有 pl_cli `.so`，没有该.py。因此这个特定fallback在该wheel直接部署环境中不可用。正式console命令存在时走正常分支。
4. **保留/重跑行为**：宿主和缺陷的 FORCE_CONSTANTS存在时直接复用，未在这些脚本中比对参数或结构指纹（embedding658–663/968–972；nonembedding495–496）。非嵌入main最终删除 PL/bulk、PL/defect、PL/supercell（660–662），本次没有执行任何删除。
5. `PARA_FILE="$PL_INPUT_ROOT/../iLED.para"`（两子脚本6行）路径与根目录可能不一致，但子脚本主要使用父脚本传来的PL_环境变量；不能仅凭这一赋值宣称整个流程读取错误。编译PL helper是否读取PARA_FILE仍未知。

本文解答了身份、打包入口、可见Python导出、PL脚本流程、模板和资源；其他编译阶段的具体算法、守卫机制、结果精度和真实集群运行情况仍未验证。
