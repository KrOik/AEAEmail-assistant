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
    
    if (!apiKey) {
      console.error('缺少QWEN_API_KEY环境变量');
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ error: '服务器配置错误：缺少API密钥' })
      };
    }
    
    // 确保API_URL是完整的端点URL
    // 根据官方文档，正确的URL格式为：https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
    let apiUrl = process.env.API_URL || 'https://dashscope.aliyuncs.com/compatible-mode/v1';
    
    // 确保URL以/chat/completions结尾
    if (!apiUrl.endsWith('/chat/completions')) {
      // 如果URL已经包含/compatible-mode/v1，但没有/chat/completions，则添加
      if (apiUrl.includes('/compatible-mode/v1') && !apiUrl.endsWith('/compatible-mode/v1')) {
        apiUrl = `${apiUrl}/chat/completions`;
      } 
      // 如果URL以/compatible-mode/v1结尾，添加/chat/completions
      else if (apiUrl.endsWith('/compatible-mode/v1')) {
        apiUrl = `${apiUrl}/chat/completions`;
      }
      // 其他情况，使用默认完整URL
      else {
        apiUrl = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions';
      }
    }
    
    console.log('使用API URL:', apiUrl);

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
    console.log('调用API:', apiUrl);
    console.log('请求体:', JSON.stringify(requestBody));
    
    const response = await fetch(apiUrl, requestOptions);
    
    // 检查响应状态
    if (!response.ok) {
      const errorText = await response.text();
      console.error('API响应错误:', response.status, errorText);
      return {
        statusCode: response.status,
        headers,
        body: JSON.stringify({ 
          error: `API响应错误: ${response.status}`, 
          details: errorText 
        })
      };
    }
    
    // 解析JSON响应
    const responseText = await response.text();
    console.log('API响应:', responseText);
    
    let data;
    try {
      data = JSON.parse(responseText);
    } catch (parseError) {
      console.error('JSON解析错误:', parseError, '原始响应:', responseText);
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ 
          error: `JSON解析错误: ${parseError.message}`, 
          rawResponse: responseText.substring(0, 500) // 限制长度
        })
      };
    }

    // 返回API响应
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(data)
    };
  } catch (error) {
    console.error('API调用错误:', error);
    
    // 提供更详细的错误信息
    let errorDetails = {
      message: error.message,
      type: error.type || 'unknown'
    };
    
    // 如果是网络错误，添加更多信息
    if (error.name === 'FetchError') {
      errorDetails.url = apiUrl;
      errorDetails.code = error.code;
    }
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        error: `API调用失败: ${error.message}`,
        details: errorDetails
      })
    };
  }
};