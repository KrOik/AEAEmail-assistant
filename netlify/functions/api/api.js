// Netlify函数处理API调用
// 导入fetch API，在Node.js环境中需要显式导入
const fetch = require('node-fetch');

exports.handler = async function(event, context) {
  // 设置CORS头
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS'
  };

  // 处理预检请求
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    };
  }

  // 只允许POST请求
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: '只支持POST方法' })
    };
  }

  try {
    // 解析请求体
    const requestBody = JSON.parse(event.body);
    
    // 获取环境变量
    const apiKey = process.env.QWEN_API_KEY;
    const apiUrl = process.env.API_URL;
    
    if (!apiKey || !apiUrl) {
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ error: '服务器配置错误：缺少API密钥或URL' })
      };
    }

    // 构建请求选项
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify(requestBody)
    };

    // 调用API
    const response = await fetch(apiUrl, requestOptions);
    const data = await response.json();

    // 返回API响应
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(data)
    };
  } catch (error) {
    console.error('API调用错误:', error);
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: `API调用失败: ${error.message}` })
    };
  }
};