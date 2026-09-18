# 一、数据推送 

## **1** 数据推送（异步） 

|参数|类型|是否必填|描述|示例值|
|---|---|---|---|---|
|task_id|String|否|任务 ID||
|meterNo|String|是|电表编号||
|sjsj|String|是|数据时间||
|yxzt|String|否|运行状态(未启用)||
|sjzt|String|否|事件告警||
|jdqzt|String|是|继电器状态|00120001-合闸00120002-拉闸|
|axdy|number|否|A相电压(V)||
|bxdy|number|否|B相电压(V)||
|cxdy|number|否|C相电压(V)||
|axdl|number|否|A相电流(A)||
|bxdl|number|否|B相电流(A)||
|cxdl|number|否|C相电流(A)||
|sydl|number|否|剩余电流(A)||
|zyggl|number|否|总有功功率(kW)||

|参数|类型|是否必填|描述|
|---|---|---|---|
|axyggl|number|否|A相有功功率(kW)|
|bxyggl|number|否|B相有功功率(kW)|
|cxyggl|number|否|C相有功功率(kW)|
|zwggl|number|否|总无功功率(kvar)|
|axwggl|number|否|A相无功功率(kvar)|
|bxwggl|number|否|B相无功功率(kvar)|
|cxwggl|number|否|C相无功功率(kvar)|
|zglys|number|否|总功率因数|
|axglys|number|否|A相功率因数|
|bxglys|number|否|B相功率因数|
|cxglys|number|否|C相功率因数|
|zxygzdl|number|是|正向有功总电量(kWh)|
|zxygzdl1|number|否|正向有功费率1电量(kWh)|
|zxygzdl2|number|否|正向有功费率2电量(kWh)|
|zxygzdl3|number|否|正向有功费率3电量(kWh)|

|参数|类型|是否必填|描述|
|---|---|---|---|
|zxygzdl4|number|否|正向有功费率3电量(kWh)|
|axwd|number|否|A相温度(℃)|
|bxwd|number|否|B相温度(℃)|
|cxwd|number|否|C相温度(℃)|
|lxwd|number|否|零线温度(℃)|
|hjwd|number|否|环境温度(℃)|

### 告警事件 

|**code**|事件|
|---|---|
|C0001|A相过压|
|C0002|B相过压|
|C0003|C相过压|
|C0004|A相过流|
|C0005|B相过流|
|C0006|C相过流|
|C0007|A相起弧|
|C0008|B相起弧|
|C0009|C相起弧|
|C0010|A相过温度|
|C0011|B相过温度|
|C0012|C相过温度|

|**code**|事件|
|---|---|
|C0013|零线过温度|
|C0014|环境温度超|
|C0015|恶性负载|
|C0016|剩余电流|
|C0017|三相电流不平衡|
|C0018|电压不平衡|
|C0022|温度故障|
|C0023|剩余电流故障|

### 推送案例

( 不同表计 data 内容略有不同，参数名称不变 ) ： 

```
{
	"data": {
		"zwggl": 0.007,
		"zyggl": 0.0036,
		"bxdy": 0,
		"bxwggl": 0,
		"bxyggl": 0,
		"cxglys": 0,
		"axdl": 0.035,
		"cxdl": 0,
		"bxglys": 0,
		"meterNo": "0",
		"sydl": 0,
		"sjsj": 1595260808000,
		"zglys": 0.458,
		"yxzt": "00000000",
		"axdy": 240.5,
		"zxygzdl": 83.97,
		"zxygzdl1": 83.97,
		"cxdy": 0,
		"zxygzdl3": 0,
		"zxygzdl2": 0,
		"axglys": 0.429,
		"zxygzdl4": 0,
		"cxwggl": 0,
		"cxyggl": 0,
		"bxdl": 0,
		"axyggl": 0.0036,
		"axwggl": 0.007,
		"jdqzt": "00120001",
		"hjwd": 21
    	},
	"meterNo": "611391900110"
  }
```

### 小时任务 

```json
{
    "data": [
        {
            "yxzt": "00000000",
            "axdy": 236.7,
            "zxygzdl": 7.44,
            "zyggl": 0,
            "zxygzdl1": 7.44,
            "zxygzdl3": 0,
            "zxygzdl2": 0,
            "axglys": 0,
            "zxygzdl4": 0,
            "axdl": 0,
            "axyggl": 0,
            "jdqzt": "00120002",
            "meterNo": "252012101009",
            "sydl": 0,
            "sjsj": 1612502100000,
            "zglys": 0
        },
        {
            "yxzt": "00000000",
            "axdy": 236.8,
            "zxygzdl": 7.44,
            "zyggl": 0,
            "zxygzdl1": 7.44,
            "zxygzdl3": 0,
            "zxygzdl2": 0,
            "axglys": 0,
            "zxygzdl4": 0,
            "axdl": 0,
            "axyggl": 0,
            "jdqzt": "00120002",
            "meterNo": "252012101009",
            "sydl": 0,
            "sjsj": 1612503000000,
            "zglys": 0
        },
        {
            "yxzt": "00000000",
            "axdy": 237.5,
            "zxygzdl": 7.44,
            "zyggl": 0,
            "zxygzdl1": 7.44,
            "zxygzdl3": 0,
            "zxygzdl2": 0,
            "axglys": 0,
            "zxygzdl4": 0,
            "axdl": 0,
            "axyggl": 0,
            "jdqzt": "00120002",
            "meterNo": "252012101009",
            "sydl": 0,
            "sjsj": 1612503900000,
            "zglys": 0
        },
        {
            "yxzt": "00000000",
            "axdy": 237.2,
            "zxygzdl": 7.44,
            "zyggl": 0,
            "zxygzdl1": 7.44,
            "zxygzdl3": 0,
            "zxygzdl2": 0,
            "axglys": 0,
            "zxygzdl4": 0,
            "axdl": 0,
            "axyggl": 0,
            "jdqzt": "00120002",
            "meterNo": "252012101009",
            "sydl": 0,
            "sjsj": 1612504800000,
            "zglys": 0
        }
    ],
    "meterNo": "252012101009"
}
```

### 错误码 

|**code**（返回码）|**msg**（返回码描述）|
|---|---|
|0|接口调用成功，调用结果请参考具体的API文档所对应的业务返回参数|
|20001|表计已存在召测任务|

# 二、表计数据查询 

### 描述 

表计数据查询 

### 请求地址 

|环境|**http** 请求地址|
|---|---|
|正式环境|http://bd01.bbicloud.com:9001<br>/iot/data/queryMeterData|
|请求方式|post|

### **HEADER** 参数 

|参数|类型|是否必填|描述|示例值|
|---|---|---|---|---|
|token|**string**|是|加密值|JwtToken算法生成<br /> Subject:<br />Issuer:|
|projectId|**Long**|是|项目标识||

### 请求参数（ **Json** 格式） 

**Json** 格式请求参数实例 **:** 

|参数|类型|是否必填|描述|示例值|
|---|---|---|---|---|
|meter_no|String|否|表号|212005100172|
|start_time|String|是|开始时间|2020-08-15 10:00:00|
|end_time|String|是|结束时间|2020-08-15 20:00:00|

### 响应参数 

#### **Json** 格式响应参数实例 **:** 

```json
{
    "code": 0,
    "status": 0,
    "msg": "操作成功",
    "data": [
        {
            "sjsj": "2020-09-17 09:00:00.000",
            "jssj": "2020-09-17 09:19:06.804",
            "yxzt": "00000000",
            "sjzt": {},
            "jdqzt": "00120001",
            "axdy": 230.39999,
            "bxdy": 0,
            "cxdy": 0,
            "axdl": 0,
            "bxdl": {},
            "cxdl": {},
            "sydl": 0,
            "zyggl": 0,
            "axyggl": 0,
            "bxyggl": 0,
            "cxyggl": 0,
            "zwggl": 0,
            "axwggl": 0,
            "bxwggl": 0,
            "cxwggl": 0,
            "zglys": 0,
            "axglys": 0,
            "bxglys": 0,
            "cxglys": 0,
            "zxygzdl": 737.39001,
            "zxygzdl1": 737.39001,
            "zxygzdl2": 0,
            "zxygzdl3": 0,
            "zxygzdl4": 0,
            "axwd": 27.4,
            "bxwd": {},
            "cxwd": {},
            "lxwd": 27.2,
            "hjwd": 29.6,
            "meter_no": "611512000209",
            "project_id": "202001120000000001",
            "gateway_no": "611512000209",
            "meter_type": "00080001"
        }]
}
```

|参数|类型|是否必填|描述|示例值|
|---|---|---|---|---|
|status|String|是|状态代码|200|
|data|json|是||project_id:项目编号<br>meter_no:表号<br />其他参数同上定义|
|msg|String|是|返回值|请求成功|

# 三、抄表 

### 描述 

抄表查询 

### 请求地址 

|环境|**http** 请求地址|
|---|---|
|正式环境|http://bd01.bbicloud.com:9001<br>/iot/callTermTask|
|请求方式|post|

### **HEADER** 参数 

|参数|类型|是否必填|描述|示例值|
|---|---|---|---|---|
|token|**string**|是|加密值|**JwtToken** 算法生成<br />Subject：<br>Issuer:|
|projectId|**Long**|是|项目标识||

### 请求参数（ **Json** 格式） 

**Json** 格式请求参数实例 **:** 

```
{"meter_no":"282004306003"} 
```

|参数|类型|是否必填|描述|示例值|
|---|---|---|---|---|
|meter_no|String|否|表号|212005100172|

### 响应参数 

#### **Json** 格式响应参数实例 **:** 

```json
{
    "code": 0,
    "status": 0,
    "msg": "操作成功",
    "data": {
        "task_id": "u3ndfi81hkjvjp1070akrj4cis",
				"meter_no":"271911104149"
    }
}
```

|参数|类型|是否必填|描述|示例值|
|---|---|---|---|---|
|status|String|是|状态代码|200|
|data|json|是||task_id:任务编号<br>meter_no:表号|
|msg|String|是|返回值|请求成功|

# 四、拉闸 

### 描述 

拉闸 

### 请求地址 

|环境|**http** 请求地址|
|---|---|
|正式环境|http://bd01.bbicloud.com:9001/iot/disconnectMeter|
|请求方式|post|

### **HEADER** 参数 

|参数|类型|是否必填|描述|示例值|
|---|---|---|---|---|
|token|**string**|是|加密值|**JwtToken** 算法生成<br />Subject:<br /> Issuer:|
|projectId|**Long**|是|项目标识||

### 请求参数（ **Json** 格式） 

**Json** 格式请求参数实例 **:** 

```json
{"meter_no":"282004306003"} 
```

|参数|类型|是否必填|描述|示例值|
|---|---|---|---|---|
|meter_no|String|否|表号|212005100172|



### 响应参数 

#### **Json** 格式响应参数实例 **:** 

```json
{
    "code": 0,
    "status": 0,
    "msg": "操作成功",
    "data": {
        "meter_no": "271911104149",
        "task_id": "qgtknffcukj55rioahple7va12"
    }
}

```

|参数|类型|是否必填|描述|示例值|
|---|---|---|---|---|
|status|String|是|状态代码|200|
|data|json|是||task_id:任务编号<br>meter_no:表号|
|msg|String|是|返回值|请求成功|

# 五、合闸 

### 描述 

拉闸 

### 请求地址 

|环境|**http** 请求地址|
|---|---|
|正式环境|http://bd01.bbicloud.com:9001/iot/connectMeter|
|请求方式|post|

### **HEADER** 参数 

|参数|类型|是否必填|描述|示例值|
|---|---|---|---|---|
|token|**string**|是|加密值|**JwtToken** 算法生成<br />Subject：<br>Issuer:|
|projectId|**Long**|是|项目标识||

### 请求参数（ **Json** 格式） 

**Json** 格式请求参数实例 **:** 

```json
{"meter_no":"282004306003"} 
```

|参数|类型|是否必填|描述|示例值|
|---|---|---|---|---|
|meter_no|String|否|表号|212005100172|

### 响应参数 

#### **Json** 格式响应参数实例 **:** 

```json
{
  "code": 0,
  "status": 0,
  "msg": "操作成功",
  "data": {
			"meter_no": "271911104149",
			"task_id": "qgtknffcukj55rioahple7va12"
  }
}
```

|参数|类型|是否必填|描述|示例值|
|---|---|---|---|---|
|status|String|是|状态代码|200|
|data|json|是||task_id:任务编号<br>meter_no:表号|
|msg|String|是|返回值|请求成功|



# 五、任务结果查询接口 

### 描述 

拉闸 

### 请求地址 

|环境|**http** 请求地址|
|---|---|
|正式环境|http://bd01.bbicloud.com:9001/iot/queryTaskData|
|请求方式|post|

### **HEADER** 参数 

|参数|类型|是否必填|描述|示例值|
|---|---|---|---|---|
|token|**string**|是|加密值|**JwtToken** 算法生成<br>Subject：<br>Issuer:|
|projectId|**Long**|是|项目标识||

### 请求参数（ **Json** 格式） 

**Json** 格式请求参数实例 **:** 

```json
{"meter_no":"282004306003"
	,"task_id": "22f9t570logrdr2qp03gspspih"
}
```

|参数|类型|是否必填|描述|示例值|
|---|---|---|---|---|
|meter_no|String|是|表号|212005100172|
|task_id|String|是|任务ID|22f9t570logrdr2qp03gspspih|

### 响应参数 

#### **Json** 格式响应参数实例 **:** 

```json
{
    "code": 0,
    "status": 0,
    "msg": "操作成功",
    "data": {
        "zwggl": 1.9965,
        "zyggl": 2.1475,
        "bxdy": 235.6,
        "bxwggl": 0.6532,
        "bxyggl": 0.81,
        "cxglys": 0.72,
        "axdl": 4.283,
        "cxdl": 3.548,
        "bxglys": 0.776,
        "meterNo": "282004306003",
        "sydl": 0,
        "sjsj": 1612508381000,
        "zglys": 0.732,
        "yxzt": "00000000",
        "axdy": 239.4,
        "zxygzdl": 3359.89,
        "zxygzdl1": 3359.89,
        "cxdy": 246.4,
        "zxygzdl3": 0,
        "zxygzdl2": 0,
        "axglys": 0.69,
        "zxygzdl4": 0,
        "cxwggl": 0.6044,
        "cxyggl": 0.6297,
        "bxdl": 4.424,
        "axyggl": 0.7077,
        "axwggl": 0.7388,
        "jdqzt": "00120001"
    }
}
```

|参数|类型|是否必填|描述|示例值|
|---|---|---|---|---|
|status|String|是|状态代码|200|
|data|json|是||task_id:任务编号; meter_no:表号|
|msg|String|是|返回值|请求成功|



