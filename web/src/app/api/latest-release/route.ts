import { NextResponse } from 'next/server';

interface GitHubReleaseAsset {
  url: string;
  id: number;
  node_id: string;
  name: string;
  label: string;
  uploader: {
    login: string;
    id: number;
    node_id: string;
    avatar_url: string;
    gravatar_id: string;
    url: string;
    html_url: string;
    followers_url: string;
    following_url: string;
    repos_url: string;
    events_url: string;
    received_events_url: string;
    type: string;
    site_admin: boolean;
  };
  content_type: string;
  state: string;
  size: number;
  download_count: number;
  created_at: string;
  updated_at: string;
  browser_download_url: string;
}

interface GitHubRelease {
  url: string;
  assets_url: string;
  upload_url: string;
  html_url: string;
  id: number;
  node_id: string;
  tag_name: string;
  target_commitish: string;
  name: string;
  draft: boolean;
  prerelease: boolean;
  created_at: string;
  published_at: string;
  description: string;
  size: number;
  assets: GitHubReleaseAsset[];
}

export const runtime = "nodejs";

export async function GET() {
  try {
    const token = process.env.GITHUB_TOKEN;
    
    const response = await fetch('https://api.github.com/repos/SiegAxel/EncryptU/releases/latest', {
      headers: {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'EncryptU-AutoDownload/1.0',
        ...(token && { 'Authorization': `token ${token}` }),
      },
    });

    if (!response.ok) {
      throw new Error(`GitHub API responded with status: ${response.status}`);
    }

    const release: GitHubRelease = await response.json();
    
    // Extract Windows installer asset
    const windowsInstaller = release.assets.find((asset) =>
      asset.name.toLowerCase().includes('.exe') || 
      asset.name.toLowerCase().includes('setup') ||
      asset.name.toLowerCase().includes('installer')
    );

    if (!windowsInstaller) {
      throw new Error('No Windows installer found in latest release');
    }

    return NextResponse.json({
      success: true,
      data: {
        version: release.tag_name,
        name: release.name,
        description: release.description,
        published_at: release.published_at,
        download_url: windowsInstaller.browser_download_url,
        file_name: windowsInstaller.name,
        file_size: windowsInstaller.size,
        download_count: windowsInstaller.download_count,
        html_url: release.html_url,
      }
    });
  } catch (error) {
    console.error('Error fetching latest release:', error);
    
    // Return fallback data
    return NextResponse.json({
      success: false,
      error: 'Failed to fetch latest release',
      fallback: {
        version: 'v1.0.0',
        download_url: 'https://github.com/SiegAxel/EncryptU/releases',
        file_name: 'EncryptU-Setup-v1.0.0.exe',
        file_size: '39 MB'
      }
    });
  }
}