import { useMemo, useState } from 'react';
import { Button, Col, Input, Row, Select, Table } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { useMeters } from '../../api/queries';
import type { MeterRow } from '../../api/types';

function relativeTime(sampleTime: string): string {
  if (!sampleTime) return '—';
  const then = new Date(sampleTime.replace(' ', 'T')).getTime();
  const diffMs = Date.now() - then;
  const min = Math.floor(diffMs / 60000);
  if (min < 1) return '刚刚';
  if (min < 60) return `${min}分钟前`;
  const hour = Math.floor(min / 60);
  if (hour < 24) return `${hour}小时前`;
  const day = Math.floor(hour / 24);
  if (day < 30) return `${day}天前`;
  const month = Math.floor(day / 30);
  if (month < 12) return `${month}个月前`;
  const year = Math.floor(month / 12);
  return `${year}年前`;
}

export function MeterTab() {
  const meters = useMeters();
  const [category, setCategory] = useState('全部分类');
  const [search, setSearch] = useState('');

  const categories = meters.data?.categories ?? ['全部分类'];

  const filtered = useMemo(() => {
    let rows = meters.data?.rows ?? [];
    if (category !== '全部分类') rows = rows.filter((r) => r.category === category);
    if (search.trim()) {
      const kw = search.trim().toLowerCase();
      rows = rows.filter(
        (r) => r.roomDetailAddr.toLowerCase().includes(kw) || r.meterNo.toLowerCase().includes(kw),
      );
    }
    return [...rows].sort((a, b) => (a.roomDetailAddr < b.roomDetailAddr ? -1 : 1));
  }, [meters.data, category, search]);

  const columns = [
    { title: '电表编号', dataIndex: 'meterNo', key: 'meterNo', width: 130 },
    { title: '安装位置 / 点位名称', dataIndex: 'roomDetailAddr', key: 'roomDetailAddr', ellipsis: true },
    { title: '用电分类', dataIndex: 'category', key: 'category', width: 100 },
    {
      title: '互感器倍率',
      dataIndex: 'rate',
      key: 'rate',
      width: 100,
      align: 'right' as const,
      render: (v: number) => `${Math.round(v)}x`,
    },
    { title: 'CT/PT规格', dataIndex: 'ctRate', key: 'ctRate', width: 110 },
    {
      title: '折算真实底数(kWh)',
      dataIndex: 'realKwh',
      key: 'realKwh',
      width: 150,
      align: 'right' as const,
      render: (v: number) => v.toFixed(2),
    },
    {
      title: '实时负荷(kW)',
      dataIndex: 'powerKw',
      key: 'powerKw',
      width: 120,
      align: 'right' as const,
      render: (v: number) => v.toFixed(2),
    },
    {
      title: '继电器状态',
      dataIndex: 'relayStatusDesc',
      key: 'relayStatusDesc',
      width: 110,
      render: (v: string) => <span style={{ color: v.includes('通电') ? '#059669' : '#dc2626', fontWeight: 600 }}>{v}</span>,
    },
    {
      title: '在线状态',
      dataIndex: 'onlineStatusDesc',
      key: 'onlineStatusDesc',
      width: 90,
      render: (v: string) => <span style={{ color: v === '在线' ? '#059669' : '#d97706' }}>{v}</span>,
    },
    {
      title: '最新采样时间',
      dataIndex: 'sampleTime',
      key: 'sampleTime',
      width: 140,
      render: (v: string) => relativeTime(v),
    },
  ];

  return (
    <div className="section-box">
      <div className="section-title">
        <span>⚡ 24 块智能物联电表台账与工况全览</span>
        <span style={{ fontSize: 12, color: '#059669', fontWeight: 400 }}>单表最新工况台账（每表一条，共 24 台在运）</span>
      </div>
      <div className="section-sub">
        包含互感器变比规格、最新底数读数及继电器通断状态
      </div>

      <Row gutter={12} style={{ marginBottom: 14 }}>
        <Col span={5}>
          <Select
            style={{ width: '100%' }}
            value={category}
            onChange={setCategory}
            options={categories.map((c) => ({ value: c, label: c }))}
          />
        </Col>
        <Col span={15}>
          <Input
            placeholder="输入点位名称（如：花房、空调、水泵、弱电间）或表号..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            allowClear
          />
        </Col>
        <Col span={4} style={{ textAlign: 'right' }}>
          <a href="/api/export/ledger.csv" download className="ant-btn ant-btn-primary">
            <DownloadOutlined /> 导出表计台账 (CSV)
          </a>
        </Col>
      </Row>

      <Table<MeterRow>
        rowKey="meterNo"
        columns={columns}
        dataSource={filtered}
        pagination={false}
        size="small"
        loading={meters.isLoading}
        scroll={{ x: 1400 }}
      />
    </div>
  );
}
