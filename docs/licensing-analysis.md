# iLED 1.11.14 授权机制静态检查

后续更新：已根据新的修改请求部署本地启动补丁，具体改动、验证与恢复方式见 [license-patch.md](license-patch.md)。下面保留改动前的静态机制调查。

授权相关功能位于 `runtime_guard.cpython-310-x86_64-linux-gnu.so`。本次只读取符号、字符串和 ELF 布局，没有执行授权代码、读取用户的实际许可证或修改校验逻辑。

**直接观察**

- 保留 `find_activation`、`_read_activation`、`_canonical_payload`、`_verify_signature`、`verify_activation` 和 `require_activation` 函数符号。
- 可见 `Ed25519PublicKey`、`load_pem_public_key`、`InvalidSignature` 和签名缺失/无效错误文本。
- 可见字段 `payload`、`signature`、`product`、`modules`、`issued_at`、`expires_at` 及日期格式检查文本。
- 可见主机、调度器不匹配错误；`machine_id_sha256`、`server_fingerprint`、`cluster_fingerprint` 等标识常量。
- 可见许可证名 `iLED.lic` 和变量 `ILED_LICENSE_FILE`、`ILED_AUTH_FILE`、`XDG_CONFIG_HOME`。没有恢复所有默认搜索路径和变量优先级。
- 主入口可见 `--activation-request`、`--license-request` 常量；授权模块错误提示明确建议运行 `iLED --activation-request` 并联系供应方。

**对使用方式的意义**

签名、有效期、设备/集群范围和模块范围是独立的检查维度。静态材料支持“这是签名许可证”的判断；修改受签名保护的内容会导致验签失败是相应的密码学推断，尚未运行该许可证实现验证。

已有有效许可证时，可以按模块中的环境变量指定其路径，例如 `ILED_LICENSE_FILE=/absolute/path/to/iLED.lic`。尚未在目标环境执行验证。

没有许可证、许可证过期、设备迁移或新增模块时，包内提供的流程是生成 activation request，再由签发方更新许可。不要将路径配置错误与签名、期限或绑定错误混为一类。

若维护方希望发布免许可证版本，合适的开发路径是在源代码中调整主入口的授权门控和相关模块调用，重新构建匹配的 wheel，并验证命令分发与计算流程。当前调查只有编译包，尚未修改实现。

**证据**

- [静态字符串记录](runtime-guard-static-notes.json)：绑定文件偏移，普通本地工具结果。
- [REA ELF 布局](rea-runtime-guard-layout.json)：Evidence ID `ev_8c8b3f93366b7a667bbaa543e344221dde948fe82398d2b801801f6d62420b43`。
- 授权模块 SHA-256：`e7eccfa3aa6160f49c3d711bb4396c3be584380e72607f5c854760389e0c5427`。

这些结果没有建立所有授权分支的指令级可达性，也没有恢复或修改签发私钥。
