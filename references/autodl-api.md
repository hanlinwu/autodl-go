# AutoDL API Reference

Sources:
- https://www.autodl.com/docs/instance_pro_api/
- https://www.autodl.com/docs/common_api/
- https://www.autodl.com/docs/instance_data/
- https://www.autodl.com/docs/quick_start/

Host: `https://api.autodl.com`

Authentication header:

```python
headers = {"Authorization": "<token>"}
```

Token location: AutoDL console -> Account/Settings -> Developer Token. Pro API usage requires personal real-name verification or enterprise verification.

## Account

### Balance

`POST /api/v1/dev/wallet/balance`

No request parameters. Response `data` contains integer values:

- `assets`: current balance; divide by 1000 to get CNY yuan.
- `accumulate`: accumulated spend; divide by 1000 to get CNY yuan.
- `voucher_balance`: usable voucher balance; divide by 1000 to get CNY yuan.

## Pro Instances

### Create Instance

`POST /api/v1/dev/instance/pro/create`

Default billing is pay-as-you-go; the API documentation says other billing modes are not currently supported for this create endpoint.

Body fields:

- `data_center_list` optional array. Omit to let AutoDL choose. Known examples: `westDC3` for Northwest, `beijingDC2` for Beijing.
- `req_gpu_amount` required integer from 1 to 4.
- `expand_system_disk_by_gb` required integer from 0 to 500.
- `gpu_spec_uuid` required. See GPU spec table below.
- `image_uuid` required. Use a private image UUID or a public base image UUID.
- `cuda_v_from` required integer CUDA floor. Example: `113` means CUDA >= 11.3; `118` means CUDA >= 11.8.
- `instance_name` optional display/remark name.
- `start_command` optional command run after boot. Failure does not stop the instance.

Typical body:

```json
{
  "data_center_list": ["westDC3", "beijingDC2"],
  "req_gpu_amount": 1,
  "expand_system_disk_by_gb": 0,
  "gpu_spec_uuid": "pro6000-p",
  "image_uuid": "base-image-l2t43iu6uk",
  "cuda_v_from": 118,
  "instance_name": "experiment",
  "start_command": "sleep 1"
}
```

Returns the new instance UUID in `data`, for example `pro-76419909953e`.

### List Instances

`POST /api/v1/dev/instance/pro/list`

Body:

```json
{"page_index": 1, "page_size": 20}
```

Useful fields in `data.list[]`: `uuid`, `region_sign`, `region_name`, `status`, `sub_status`, `start_mode`, `charge_type`, `req_gpu_amount`, `started_at`, `stopped_at`, `name`, `gpu_spec_uuid`.

### Status

`GET /api/v1/dev/instance/pro/status`

Body:

```json
{"instance_uuid": "pro-..."}
```

Response `data` is the instance status string, such as `running`.

### Snapshot

`GET /api/v1/dev/instance/pro/snapshot`

Body:

```json
{"instance_uuid": "pro-..."}
```

Useful fields: `payg_price`, `origin_pay_price`, `snapshot_gpu_alias_name`, `chip_corp`, `cpu_arch`, `usage_info`, `ssh_command`, `proxy_host`, `root_password`, `ssh_port`, `jupyter_token`, `jupyter_domain`, `service_6006_domain`, `service_6008_domain`.

Redact `root_password`, `jupyter_token`, and private domains in chat unless the user explicitly asks to reveal them.

### Power On

`POST /api/v1/dev/instance/pro/power_on`

Body:

```json
{
  "instance_uuid": "pro-...",
  "payload": "gpu",
  "start_command": "sleep 1"
}
```

`payload` must be `gpu`; the API documentation says API no-card start is not supported. Optional `start_command` overrides the create-time command.

### Power Off

`POST /api/v1/dev/instance/pro/power_off`

Body:

```json
{"instance_uuid": "pro-..."}
```

### Release

`POST /api/v1/dev/instance/pro/release`

Body:

```json
{"instance_uuid": "pro-..."}
```

AutoDL documentation says to power off before releasing, otherwise release may fail. Released instance data is cleared and cannot be recovered.

## Images

### Save Image

`POST /api/v1/dev/instance/pro/image/save`

Body:

```json
{
  "instance_uuid": "pro-...",
  "image_name": "image-name"
}
```

Returns `data.image_uuid`; confirm save status by listing private images.

### List Private Images

`POST /api/v1/dev/instance/pro/image/private/list`

Body:

```json
{"page_index": 1, "page_size": 10}
```

Useful fields: `image_uuid`, `name`, `status`, `image_size`, `create_at`.

## Storage

### Switch Dedicated NFS/File Storage

`POST /api/v1/dev/exclusive_nfs/mount`

Body:

```json
{
  "data_center": "westDC2",
  "mountable": 1
}
```

`mountable: 1` mounts dedicated NFS and disables normal file storage. `mountable: -1` disables dedicated NFS and switches back to normal file storage. Confirm with the user before changing storage.

## GPU Spec IDs

| Display GPU | Display Spec | API `gpu_spec_uuid` |
|---|---|---|
| H800-80G | General | `h800` |
| 4090-48G | General | `v-48g` |
| PRO6000-96G | Performance | `pro6000-p` |
| 4080(S)-32G | Performance | `v-32g-p` |
| 3090-48G | General | `v-48g-350w` |
| 5090-32G | Performance | `5090-p` |
| 4090D | General | `4090D` |

## Public Base Image UUIDs

| Image UUID | Framework | Image |
|---|---|---|
| `base-image-12be412037` | PyTorch | cuda11.1-cudnn8-devel-ubuntu18.04-py38-torch1.9.0 |
| `base-image-u9r24vthlk` | PyTorch | cuda11.3-cudnn8-devel-ubuntu20.04-py38-torch1.10.0 |
| `base-image-l374uiucui` | PyTorch | cuda11.3-cudnn8-devel-ubuntu20.04-py38-torch1.11.0 |
| `base-image-l2t43iu6uk` | PyTorch/TensorRT | cuda11.8-cudnn8-devel-ubuntu20.04-py38-torch2.0.0 |
| `base-image-0gxqmciyth` | TensorFlow | cuda11.2-cudnn8-devel-ubuntu18.04-py38-tf2.5.0 |
| `base-image-uxeklgirir` | TensorFlow | cuda11.2-cudnn8-devel-ubuntu20.04-py38-tf2.9.0 |
| `base-image-4bpg0tt88l` | TensorFlow | cuda11.4-py38-tf1.15.5 |
| `base-image-mbr2n4urrc` | Miniconda | cuda11.6-cudnn8-devel-ubuntu20.04-py38 |
| `base-image-qkkhitpik5` | Miniconda | cuda10.2-cudnn7-devel-ubuntu18.04-py38 |
| `base-image-h041hn36yt` | Miniconda | cuda11.1-cudnn8-devel-ubuntu18.04-py38 |
| `base-image-7bn8iqhkb5` | Miniconda | cudagl11.3-cudnn8-devel-ubuntu20.04-py38 |
| `base-image-k0vep6kyq8` | Miniconda | cuda9.0-cudnn7-devel-ubuntu16.04-py36 |
| `base-image-l2843iu23k` | TensorRT | cuda11.8-cudnn8-devel-ubuntu20.04-py38-trt8.5.1 |

## Data and Billing Notes

- Data and environment are retained across power off and power on while the instance still exists.
- An instance may be released after 15 continuous powered-off days; all data is cleared and cannot be recovered.
- Local SSD data has no redundancy guarantee. Back up important datasets, checkpoints, and logs to file storage or local storage.
- Billing starts when instance status is `running`; power off idle instances promptly.
