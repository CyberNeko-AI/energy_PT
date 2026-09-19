import { Col, Row, Statistic } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { useOverview } from '../../api/queries';

export function SyncTab({ start, end }: { start?: string; end?: string }) {
  const overview = useOverview();
  const o = overview.data;

  const rangeQs = [start && `start=${start}`, end && `end=${end}`].filter(Boolean).join('&');

  return (
    <div className="section-box">
      <div className="section-title">⚙️ SQLite 数据库与三级同步管道监控</div>
      <div className="section-sub">本地存储状态与各级数据表行数</div>

      <Row gutter={16}>
        <Col span={6}>
          <Statistic title="数据库存储路径" value={o?.dbPath?.split('/').pop() ?? '—'} valueStyle={{ fontSize: 20 }} />
          <div style={{ fontSize: 12, color: '#7e968b' }}>体积: {o?.dbSizeKb ?? 0} KB</div>
        </Col>
        <Col span={6}>
          <Statistic title="日冻结读数 (Tier-1)" value={o?.counts?.meter_readings ?? 0} suffix="条" valueStyle={{ fontSize: 20 }} />
          <div style={{ fontSize: 12, color: '#7e968b' }}>每天归档</div>
        </Col>
        <Col span={6}>
          <Statistic title="负荷工况采样 (Tier-2)" value={o?.counts?.meter_load_samples ?? 0} suffix="条" valueStyle={{ fontSize: 20 }} />
          <div style={{ fontSize: 12, color: '#7e968b' }}>每15分钟轮询</div>
        </Col>
        <Col span={6}>
          <Statistic title="告警事件历史 (Tier-3)" value={o?.counts?.alarm_events ?? 0} suffix="条" valueStyle={{ fontSize: 20 }} />
          <div style={{ fontSize: 12, color: '#7e968b' }}>每分钟检测</div>
        </Col>
      </Row>

      <div style={{ borderTop: '1px solid #edf4f0', margin: '18px 0' }} />

      <Row gutter={16}>
        <Col span={12}>
          <div style={{ fontWeight: 700, color: '#0e4c34', marginBottom: 10 }}>📥 历史用电汇总报表下载</div>
          <a href={`/api/export/daily.csv?${rangeQs}`} download className="ant-btn ant-btn-default">
            <DownloadOutlined /> 下载每日用电量报表 (CSV)
          </a>
        </Col>
        <Col span={12}>
          <div style={{ fontWeight: 700, color: '#0e4c34', marginBottom: 10 }}>📥 分类场景用电报表下载</div>
          <a href={`/api/export/category.csv?${rangeQs}`} download className="ant-btn ant-btn-default">
            <DownloadOutlined /> 下载场景分类用电报表 (CSV)
          </a>
        </Col>
      </Row>
    </div>
  );
}
