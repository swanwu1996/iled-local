# iLED 本地学习版

iLED 1.11.14 本地学习版，适用于 Linux x86-64、Python 3.10。

## 安装

```bash
conda create -n iled python=3.10 -y
conda activate iled
git clone https://github.com/swanwu1996/iled-local.git
cd iled-local
python -m pip install .
```

安装时会自动下载 iLED 安装包及所需 Python 依赖。

## 运行

在计算目录准备 `POSCAR` 和 `iLED.para`，配置 VASP、赝势路径和集群参数后运行：

```bash
conda activate iled
cd /path/to/calculation
iLED -pre
```

`potcar_path` 请使用绝对路径。PRE 阶段使用 `cluster=local` 生成输入，使用 `cluster=slurm` 会尝试提交任务。
