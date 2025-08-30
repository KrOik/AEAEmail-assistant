// Netlify函数处理API调用
// 使用ESM模块语法导入fetch API
import fetch from 'node-fetch';
import { setGlobalDispatcher, ProxyAgent } from 'undici';

// 设置全局超时时间更长的代理
const agent = new ProxyAgent({
  connect: {
    timeout: 60000 // 60秒连接超时
  },
  request: {
    timeout: 60000 // 60秒请求超时
  }
});
setGlobalDispatcher(agent);

export const handler = async function(event, context) {
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
    
    // 添加超时控制
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30秒超时
    
    try {
      requestOptions.signal = controller.signal;
      const response = await fetch(apiUrl, requestOptions);
      clearTimeout(timeoutId); // 清除超时计时器
    
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
    } catch (fetchError) {
      clearTimeout(timeoutId);
      console.error('API请求错误:', fetchError);
      
      // 处理超时错误
      if (fetchError.name === 'AbortError') {
        return {
          statusCode: 504,
          headers,
          body: JSON.stringify({ 
            error: '请求超时', 
            details: '服务器在规定时间内未响应，请稍后重试'
          })
        };
      }

      // 返回API响应
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify(data)
      };
    }
  } catch (error) {
    console.error('API调用错误:', error);
    
    // 提供更详细的错误信息
    let errorDetails = {
      message: error.message,
      type: error.type || error.name || 'unknown'
    };
    
    // 如果是网络错误，添加更多信息
    if (error.name === 'FetchError' || error.name === 'TypeError') {
      errorDetails.url = apiUrl;
      errorDetails.code = error.code;
    }
    
    // 处理punycode相关错误
    if (error.message && error.message.includes('punycode')) {
      console.warn('检测到punycode弃用警告，这是一个Node.js内部警告，不影响功能');
    }
    
    return {
      statusCode: 504, // 使用504表示网关超时
      headers,
      body: JSON.stringify({ 
        error: `API调用失败: ${error.message}`,
        details: errorDetails
      })
    };
  }
};