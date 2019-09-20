SELECT 
	p.[HostName], 
	p.[ProcessID],
	s.[Name],
	r.[State],
	DATEDIFF(minute, r.[Created], GETUTCDATE()) AS RuntimeInMinutes,
	DATEDIFF(minute, r.[Created], GETUTCDATE())/60.00 AS RuntimeInHours,
	DATEDIFF(minute, p.[Created], GETUTCDATE()) AS ProcessUptimeInMinutes,
	r.[Created],
	r.[CurrentSkillName],
	r.[AgentHostProcessID],
	r.[SubscriptionID]
FROM 
	[IASDB].[dbo].[BO_SubscriptionRuntime] AS r
	INNER JOIN 
	[IASDB].[dbo].[BO_Subscription] AS s
	ON r.[SubscriptionID] = s.[SubscriptionID]
	RIGHT JOIN [IASDB].[dbo].[BO_AgentHostProcess] AS p
	ON r.[AgentHostProcessID] = p.[AgentHostProcessID]
ORDER BY 
	p.[HostName], p.[ProcessID]

