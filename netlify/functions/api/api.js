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
    // 根据官方文档，正确的URL格式为阿里云百炼通义千问的OpenAI兼容接口URL
    let apiUrl = process.env.API_URL || '阿里云百炼通义千问的OpenAI兼容接口基础URL';
    
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
        apiUrl = '阿里云百炼通义千问的OpenAI兼容接口完整URL';
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
    
    // 设置超时处理
    const timeout = 60000; // 60秒超时
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    // 添加abort信号到请求选项
    requestOptions.signal = controller.signal;
    
    // 添加重试机制
    let retries = 2;
    let response;
    
    try {
      while (retries >= 0) {
        try {
          response = await fetch(apiUrl, requestOptions);
          break; // 成功获取响应，跳出循环
        } catch (fetchError) {
          if (fetchError.name === 'AbortError') {
            throw new Error('请求超时，请稍后再试');
          }
          
          if (retries === 0) {
            throw fetchError; // 重试次数用完，抛出错误
          }
          
          console.log(`API请求失败，剩余重试次数: ${retries}`);
          retries--;
          // 等待一段时间后重试
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      }
    } finally {
      clearTimeout(timeoutId); // 清除超时计时器
    }
    
    // 检查响应状态
    if (!response || !response.ok) {
      const status = response ? response.status : 504;
      const statusText = response ? response.statusText : 'Gateway Timeout';
      console.error('API响应错误:', status, statusText);
      
      let errorText = '请求超时或服务暂时不可用';
      if (response) {
        try {
          errorText = await response.text();
          console.error('错误详情:', errorText);
        } catch (e) {
          console.error('无法获取错误详情:', e);
        }
      }
      
      return {
        statusCode: status,
        headers,
        body: JSON.stringify({
          error: `API调用失败: ${status} ${statusText}`,
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

    // 确保API响应中的换行符被正确处理
    // 如果响应中包含文本内容，确保换行符被保留
    if (data && data.choices && data.choices.length > 0 && data.choices[0].message && data.choices[0].message.content) {
      // 保留原始换行符，前端会处理Markdown渲染
      const content = data.choices[0].message.content;
      data.choices[0].message.content = content;
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